from .model_client import ModelClient
from .workspace import Workspace

SYSTEM_PROMPT = """You are StormCodAI, an AI coding agent.

Your job is to help build software. Be precise and practical.
When asked to modify code, inspect the workspace context first and return a concise plan followed by the exact changes needed.
Do not claim that files were changed unless the application actually applies them.
""" 

class CodingAgent:
    def __init__(self, client: ModelClient, workspace: Workspace):
        self.client = client
        self.workspace = workspace

    def ask(self, request: str) -> str:
        files = self.workspace.list_files()
        context = "Workspace files:\n" + ("\n".join(files) if files else "(empty)")
        return self.client.chat(SYSTEM_PROMPT, context + "\n\nUser request:\n" + request)
