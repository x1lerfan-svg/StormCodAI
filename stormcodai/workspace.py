from pathlib import Path

class Workspace:
    def __init__(self, root: str = "stormcodai_workspace"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe(self, relative: str) -> Path:
        target = (self.root / relative).resolve()
        if target != self.root and self.root not in target.parents:
            raise ValueError("Path escapes the StormCodAI workspace.")
        return target

    def list_files(self):
        return [str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file()]

    def read(self, relative: str) -> str:
        return self._safe(relative).read_text(encoding="utf-8")

    def write(self, relative: str, content: str) -> None:
        target = self._safe(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
