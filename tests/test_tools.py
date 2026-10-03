import tempfile
import unittest

from stormcodai.tools import ToolRegistry
from stormcodai.workspace import Workspace


class ToolRegistryTests(unittest.TestCase):
    def test_only_explicit_tools_are_exposed(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = ToolRegistry(Workspace(tmp))
            self.assertEqual(registry.names(), ["list_files", "read_file"])
            with self.assertRaises(ValueError):
                registry.call("write_file", relative="x.txt", content="bad")

    def test_read_file_tool(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Workspace(tmp)
            workspace.write("hello.txt", "hello")
            registry = ToolRegistry(workspace)
            self.assertEqual(registry.call("read_file", relative="hello.txt"), "hello")
