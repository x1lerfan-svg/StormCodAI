import unittest

from stormcodai.server import validate_bind_host


class BindHostTests(unittest.TestCase):
    def test_allows_loopback_ipv4(self):
        self.assertEqual(validate_bind_host("127.0.0.1"), "127.0.0.1")

    def test_allows_loopback_ipv6(self):
        self.assertEqual(validate_bind_host("::1"), "::1")

    def test_allows_localhost(self):
        self.assertEqual(validate_bind_host("localhost"), "localhost")

    def test_rejects_public_ip(self):
        with self.assertRaises(ValueError):
            validate_bind_host("0.0.0.0")

    def test_rejects_private_non_loopback_ip(self):
        with self.assertRaises(ValueError):
            validate_bind_host("192.168.1.10")

    def test_rejects_hostname(self):
        with self.assertRaises(ValueError):
            validate_bind_host("stormcodai.local")
