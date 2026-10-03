import tempfile
import unittest

from stormcodai.agent import CodingAgent
from stormcodai.workspace import Workspace


class FakeClient:
    def __init__(self):
        self.user_prompt = ""

    def chat(self, system, user):
        self.user_prompt = user
        return "ok"


class AgentTests(unittest.TestCase):
    def test_empty_request_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent = CodingAgent(FakeClient(), Workspace(tmp))
            with self.assertRaises(ValueError):
                agent.ask("   ")

    def test_context_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Workspace(tmp)
            workspace.MAX_CONTEXT_BYTES = 1000
            workspace.write("large.txt", "x" * 2000)
            client = FakeClient()
            agent = CodingAgent(client, workspace)
            self.assertEqual(agent.ask("inspect"), "ok")
            self.assertIn("Context limit reached", client.user_prompt)
