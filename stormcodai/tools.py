from dataclasses import dataclass
from typing import Callable, Any

from .workspace import Workspace


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Callable[..., Any]


class ToolRegistry:
    """Explicit allowlist of tools exposed to the agent."""

    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self._tools = {
            "list_files": Tool(
                "list_files",
                "List files inside the workspace.",
                workspace.list_files,
            ),
            "read_file": Tool(
                "read_file",
                "Read one UTF-8 text file inside the workspace.",
                workspace.read,
            ),
        }

    def names(self) -> list[str]:
        return sorted(self._tools)

    def describe(self) -> list[dict[str, str]]:
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]

    def call(self, name: str, **arguments: Any) -> Any:
        try:
            tool = self._tools[name]
        except KeyError as exc:
            raise ValueError(f"Unknown or unavailable tool: {name}") from exc
        return tool.handler(**arguments)
