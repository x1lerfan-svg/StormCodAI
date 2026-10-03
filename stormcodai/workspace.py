from pathlib import Path


class Workspace:
    """Filesystem boundary for StormCodAI operations."""

    MAX_READ_BYTES = 256 * 1024
    MAX_FILES_IN_CONTEXT = 200

    def __init__(self, root: str = "stormcodai_workspace"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe(self, relative: str) -> Path:
        if not relative or Path(relative).is_absolute():
            raise ValueError("Workspace paths must be non-empty relative paths.")
        target = (self.root / relative).resolve()
        if target != self.root and self.root not in target.parents:
            raise ValueError("Path escapes the StormCodAI workspace.")
        return target

    def list_files(self):
        files = []
        for path in self.root.rglob("*"):
            if len(files) >= self.MAX_FILES_IN_CONTEXT:
                break
            if path.is_file() and not path.is_symlink():
                files.append(str(path.relative_to(self.root)))
        return sorted(files)

    def read(self, relative: str) -> str:
        target = self._safe(relative)
        if target.is_symlink():
            raise ValueError("Symlink access is not allowed.")
        if not target.is_file():
            raise FileNotFoundError(relative)
        if target.stat().st_size > self.MAX_READ_BYTES:
            raise ValueError(f"File is larger than {self.MAX_READ_BYTES} bytes.")
        return target.read_text(encoding="utf-8")

    def write(self, relative: str, content: str) -> None:
        target = self._safe(relative)
        if target.exists() and target.is_symlink():
            raise ValueError("Symlink writes are not allowed.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
