import tempfile
import unittest
from pathlib import Path

from stormcodai.workspace import Workspace


class WorkspaceTests(unittest.TestCase):
    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace(tmp)
            with self.assertRaises(ValueError):
                ws.read("../outside.txt")

    def test_write_and_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace(tmp)
            ws.write("src/main.py", "print('ok')")
            self.assertEqual(ws.read("src/main.py"), "print('ok')")
            self.assertEqual(ws.list_files(), ["src/main.py"])

    def test_rejects_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace(tmp)
            with self.assertRaises(ValueError):
                ws.read(str(Path(tmp) / "x.txt"))

    def test_rejects_non_text_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace(tmp)
            with self.assertRaises(TypeError):
                ws.write("bad.txt", b"not text")
