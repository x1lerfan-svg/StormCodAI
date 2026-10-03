from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Callable[..., Any]


class ToolRegistry:
    """Explicit allowlist of tools exposed to StormCodAI."""

    def __init__(self, workspace):
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
            for tool in sorted(self._tools.values(), key=lambda item: item.name)
        ]

    def call(self, name: str, **arguments: Any) -> Any:
        if not isinstance(name, str) or not name:
            raise ValueError("Tool name must be a non-empty string.")
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Unknown or unavailable tool: {name}")
        return tool.handler(**arguments)
