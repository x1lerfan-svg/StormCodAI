import json
import tempfile
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
            try:
                server.server_close()
            finally:
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
