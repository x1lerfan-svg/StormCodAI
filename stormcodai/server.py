"""Local StormCodAI web/API server.

The browser talks to this server only. Provider credentials never leave the
server process. The implementation intentionally uses the Python standard
library to keep the foundation small and auditable.
"""
from __future__ import annotations

import ipaddress
import json
import mimetypes
import os
import threading
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from .agent import CodingAgent
from .config import Config
from .model_client import ModelClient
from .workspace import Workspace

MAX_BODY_BYTES = 64 * 1024
MAX_PROMPT_CHARS = 4000
RATE_LIMIT_WINDOW = 60.0
RATE_LIMIT_REQUESTS = 30
RATE_LIMIT_MAX_KEYS = 4096
REQUEST_TIMEOUT = 75.0


def validate_bind_host(host: str) -> str:
    """Allow only loopback binding until authenticated remote access exists."""
    value = host.strip()
    if not value:
        raise ValueError("STORMCODAI_HOST cannot be empty.")
    if value.lower() == "localhost":
        return value
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError(
            "STORMCODAI_HOST must be localhost or a loopback IP address."
        ) from exc
    if not address.is_loopback:
        raise ValueError(
            "StormCodAI only binds to loopback addresses until authenticated remote access is implemented."
        )
    return value


class RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            expired = [k for k, hits in self._hits.items()
                       if not hits or now - hits[-1] >= RATE_LIMIT_WINDOW]
            for old_key in expired:
                self._hits.pop(old_key, None)

            hits = [t for t in self._hits.get(key, []) if now - t < RATE_LIMIT_WINDOW]
            if len(hits) >= RATE_LIMIT_REQUESTS:
                self._hits[key] = hits
                return False
            if key not in self._hits and len(self._hits) >= RATE_LIMIT_MAX_KEYS:
                return False
            hits.append(now)
            self._hits[key] = hits
            return True


class StormServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, handler, workspace: Workspace):
        super().__init__(address, handler)
        self.workspace = workspace
        self.agent = CodingAgent(ModelClient(Config.from_env()), workspace)
        self.rate_limiter = RateLimiter()


class Handler(BaseHTTPRequestHandler):
    server: StormServer
    protocol_version = "HTTP/1.1"

    def setup(self):
        super().setup()
        self.connection.settimeout(REQUEST_TIMEOUT)

    def log_message(self, fmt, *args):
        # Do not log request targets: URLs may contain sensitive query data.
        super().log_message("%s", "request received")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.end_headers()
        self.wfile.write(body)

    def _client_key(self) -> str:
        return self.client_address[0]

    def _read_json(self) -> dict:
        raw_length = self.headers.get("Content-Length")
        if self.headers.get("Transfer-Encoding"):
            raise ValueError("Transfer-Encoding is not supported.")
        if not raw_length:
            raise ValueError("Content-Length is required.")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("Invalid Content-Length.") from exc
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("Request body is too large.")

        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json.")

        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ValueError("Incomplete request body.")
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Request body must be valid UTF-8 JSON.") from exc
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object.")
        return data

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json(HTTPStatus.OK, {"ok": True, "version": "0.1.1"})
            return
        if path == "/api/status":
            self._send_json(HTTPStatus.OK, {
                "ok": True,
                "version": "0.1.1",
                "mode": "proposal-only",
                "capabilities": {
                    "workspace_read": True,
                    "workspace_write": False,
                    "shell_execution": False,
                    "github_write": False,
                },
            })
            return
        if path == "/api/workspace":
            files = self.server.workspace.list_files()
            self._send_json(HTTPStatus.OK, {
                "files": files,
                "limits": {
                    "max_files": self.server.workspace.MAX_FILES_IN_CONTEXT,
                    "max_read_bytes": self.server.workspace.MAX_READ_BYTES,
                    "max_write_bytes": self.server.workspace.MAX_WRITE_BYTES,
                    "max_context_bytes": self.server.workspace.MAX_CONTEXT_BYTES,
                },
            })
            return
        if path == "/api/tools":
            self._send_json(HTTPStatus.OK, {"tools": self.server.agent.tools.describe()})
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/chat":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return
        if not self.server.rate_limiter.allow(self._client_key()):
            self._send_json(HTTPStatus.TOO_MANY_REQUESTS, {"error": "Rate limit exceeded."})
            return

        request_id = uuid.uuid4().hex
        try:
            data = self._read_json()
            prompt = data.get("prompt")
            if not isinstance(prompt, str):
                raise ValueError("prompt must be a string.")
            prompt = prompt.strip()
            if not prompt:
                raise ValueError("prompt cannot be empty.")
            if len(prompt) > MAX_PROMPT_CHARS:
                raise ValueError(f"prompt exceeds {MAX_PROMPT_CHARS} characters.")
            answer = self.server.agent.ask(prompt)
            self._send_json(HTTPStatus.OK, {"request_id": request_id, "answer": answer})
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"request_id": request_id, "error": str(exc)})
        except (RuntimeError, TimeoutError):
            self._send_json(HTTPStatus.BAD_GATEWAY, {
                "request_id": request_id,
                "error": "The model service could not complete the request.",
            })
        except Exception:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {
                "request_id": request_id,
                "error": "Internal server error.",
            })

    @staticmethod
    def _safe_static_target(web_root: Path, request_path: str) -> Path | None:
        """Resolve a URL path only after strict traversal validation."""
        if " " in request_path or "\" in request_path:
            return None

        relative = request_path.lstrip("/")
        candidate = PurePosixPath(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            return None

        target = (web_root / candidate).resolve()
        try:
            target.relative_to(web_root)
        except ValueError:
            return None
        return target

    def _serve_static(self, path: str) -> None:
        if path == "/":
            path = "/index.html"
        web_root = (Path(__file__).resolve().parent.parent / "web").resolve()
        target = self._safe_static_target(web_root, path)
        if target is None or not target.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return
        try:
            data = target.read_bytes()
        except OSError:
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Unable to read resource."})
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    host = validate_bind_host(os.getenv("STORMCODAI_HOST", "127.0.0.1"))
    port = int(os.getenv("STORMCODAI_PORT", "8080"))
    workspace = Workspace(os.getenv("STORMCODAI_WORKSPACE", "stormcodai_workspace"))
    server = StormServer((host, port), Handler, workspace)
    print(f"StormCodAI app: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
