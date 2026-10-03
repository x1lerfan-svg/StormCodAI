from pathlib import Path
import os
import tempfile


class Workspace:
    """Filesystem boundary for StormCodAI operations."""

    MAX_READ_BYTES = 256 * 1024
    MAX_WRITE_BYTES = 512 * 1024
    MAX_CONTEXT_BYTES = 2 * 1024 * 1024
    MAX_FILES_IN_CONTEXT = 200

    def __init__(self, root: str = "stormcodai_workspace"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe(self, relative: str) -> Path:
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError("Workspace paths must be non-empty relative paths.")
        target = (self.root / relative).resolve()
        if target != self.root and self.root not in target.parents:
            raise ValueError("Path escapes the StormCodAI workspace.")
        return target

    def list_files(self) -> list[str]:
        files: list[str] = []
        for path in self.root.rglob("*"):
            if len(files) >= self.MAX_FILES_IN_CONTEXT:
                break
            # Do not expose symlinked files at all. This also avoids leaking
            # a secret accidentally linked into the workspace.
            if path.is_file() and not path.is_symlink():
                files.append(str(path.relative_to(self.root)))
        return sorted(files)

    def read(self, relative: str) -> str:
        target = self._safe(relative)
        original = self.root / relative
        if original.is_symlink() or target.is_symlink():
            raise ValueError("Symlink access is not allowed.")
        if not target.is_file():
            raise FileNotFoundError(relative)
        if target.stat().st_size > self.MAX_READ_BYTES:
            raise ValueError(f"File is larger than {self.MAX_READ_BYTES} bytes.")
        return target.read_text(encoding="utf-8")

    def write(self, relative: str, content: str) -> None:
        if not isinstance(content, str):
            raise TypeError("File content must be text.")
        target = self._safe(relative)
        original = self.root / relative
        if original.is_symlink() or target.is_symlink():
            raise ValueError("Symlink writes are not allowed.")
        if len(content.encode("utf-8")) > self.MAX_WRITE_BYTES:
            raise ValueError(f"File is larger than {self.MAX_WRITE_BYTES} bytes.")
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=".stormcodai-", dir=target.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise
