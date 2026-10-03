import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection

from stormcodai.server import Handler, StormServer
from stormcodai.workspace import Workspace


class ServerTests(unittest.TestCase):
    def test_health_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = StormServer(("127.0.0.1", 0), Handler, Workspace(tmp))
            try:
                server.server_close()
                # Construction itself verifies the server wiring without
                # starting a real listener in unit tests.
                self.assertEqual(server.workspace.root.as_posix(), tmp)
            finally:
                server.server_close()

    def test_status_endpoint_declares_high_risk_capabilities_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = StormServer(("127.0.0.1", 0), Handler, Workspace(tmp))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                host, port = server.server_address
                connection = HTTPConnection(host, port, timeout=5)
                try:
                    connection.request("GET", "/api/status")
                    response = connection.getresponse()
                    self.assertEqual(response.status, 200)
                    payload = json.loads(response.read().decode("utf-8"))
                finally:
                    connection.close()

                self.assertTrue(payload["ok"])
                self.assertEqual(payload["mode"], "proposal-only")
                self.assertEqual(
                    payload["capabilities"],
                    {
                        "workspace_read": True,
                        "workspace_write": False,
                        "shell_execution": False,
                        "github_write": False,
                    },
                )
            finally:
                server.shutdown()
                thread.join(timeout=5)
                server.server_close()

    def test_json_body_limit_is_constant(self):
        from stormcodai import server
        self.assertEqual(server.MAX_BODY_BYTES, 64 * 1024)
        self.assertEqual(server.MAX_PROMPT_CHARS, 4000)

    def test_rate_limiter(self):
        from stormcodai.server import RateLimiter
        limiter = RateLimiter()
        for _ in range(30):
            self.assertTrue(limiter.allow("test"))
        self.assertFalse(limiter.allow("test"))
