from .model_client import ModelClient
from .tools import ToolRegistry
from .workspace import Workspace

SYSTEM_PROMPT = """You are StormCodAI, an AI coding agent.

Rules:
- Be precise, practical, and honest.
- Treat the workspace as the source of truth.
- Never claim that a file was changed unless the application actually changed it.
- Prefer small, reviewable changes.
- Identify risks, missing requirements, and tests before proposing implementation.
- Available tools are explicitly controlled by the application; never invent unavailable tools.
"""


class CodingAgent:
    def __init__(self, client: ModelClient, workspace: Workspace):
        self.client = client
        self.tools = ToolRegistry(workspace)

    def ask(self, request: str) -> str:
        request = request.strip()
        if not request:
            raise ValueError("Request cannot be empty.")

        files = self.tools.call("list_files")
        file_context = []
        for path in files:
            try:
                content = self.tools.call("read_file", relative=path)
            except (OSError, UnicodeDecodeError, ValueError):
                continue
            file_context.append(f"\n--- {path} ---\n{content}")

        context = "Workspace files:\n" + ("\n".join(files) if files else "(empty)")
        if file_context:
            context += "\n\nReadable file contents:\n" + "".join(file_context)
        return self.client.chat(SYSTEM_PROMPT, context + "\n\nUser request:\n" + request)
