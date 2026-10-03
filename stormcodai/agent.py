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
        self.workspace = workspace

    def _build_context(self) -> str:
        files = self.tools.call("list_files")
        context = ["Workspace files:", "\n".join(files) if files else "(empty)",
                   "", "Readable file contents:"]
        total_bytes = sum(len(part.encode("utf-8")) for part in context)

        for path in files:
            try:
                content = self.tools.call("read_file", relative=path)
            except (OSError, UnicodeDecodeError, ValueError):
                continue
            block = f"\n--- {path} ---\n{content}"
            block_bytes = len(block.encode("utf-8"))
            if total_bytes + block_bytes > self.workspace.MAX_CONTEXT_BYTES:
                context.append("\n[Context limit reached; remaining files omitted.]")
                break
            context.append(block)
            total_bytes += block_bytes
        return "\n".join(context)

    def ask(self, request: str) -> str:
        request = request.strip()
        if not request:
            raise ValueError("Request cannot be empty.")
        return self.client.chat(
            SYSTEM_PROMPT,
            self._build_context() + "\n\nUser request:\n" + request,
        )
