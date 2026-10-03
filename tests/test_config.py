import os
import unittest

from stormcodai.config import Config


class ConfigTests(unittest.TestCase):
    def test_defaults(self):
        old = {key: os.environ.get(key) for key in (
            "STORMCODAI_API_KEY", "STORMCODAI_BASE_URL", "STORMCODAI_MODEL"
        )}
        try:
            for key in old:
                os.environ.pop(key, None)
            config = Config.from_env()
            self.assertEqual(config.api_key, "")
            self.assertEqual(config.base_url, "https://api.openai.com/v1")
            self.assertEqual(config.model, "")
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
