import tempfile
import unittest
from pathlib import Path

from stormcodai.context import build_context, is_safe_context_path, redact_sensitive
from stormcodai.workspace import Workspace


class ContextTests(unittest.TestCase):
    def test_sensitive_paths_are_excluded(self):
        self.assertFalse(is_safe_context_path(".env"))
        self.assertFalse(is_safe_context_path(".git/config"))
        self.assertFalse(is_safe_context_path("keys/server.pem"))
        self.assertTrue(is_safe_context_path("src/main.py"))

    def test_secrets_are_redacted(self):
        text = "api_key=super-secret-value"
        self.assertIn("[REDACTED_SECRET]", redact_sensitive(text))
        self.assertNotIn("super-secret-value", redact_sensitive(text))

    def test_context_contains_relevant_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace(tmp)
            Path(tmp, "src.py").write_text("print('hello')", encoding="utf-8")
            Path(tmp, ".env").write_text("api_key=do-not-send", encoding="utf-8")
            context = build_context(ws, "fix src.py")
            self.assertIn("src.py", context)
            self.assertNotIn("do-not-send", context)


if __name__ == "__main__":
    unittest.main()
