"""Tool registry for managing available tools and their execution."""

from __future__ import annotations
import typing

from loguru import logger

if typing.TYPE_CHECKING:
    from typing import Any, Callable


class ToolRegistry:
    """Manages tool definitions and execution."""

    def __init__(self) -> None:
        self._tools: dict[str, dict[str, Any]] = {}
        self._handlers: dict[str, Callable] = {}

    def register(self, name: str, schema: dict, handler: Callable) -> None:
        """Register a tool with its schema and execution handler."""
        self._tools[name] = schema
        self._handlers[name] = handler
        logger.debug("Registered tool: {}", name)

    def get_tools(self) -> list[dict]:
        """Get all registered tools in OpenAI format."""
        return [{"type": "function", "function": tool} for tool in self._tools.values()]

    async def execute(self, name: str, arguments: dict) -> Any:
        """Execute a tool by name with the provided arguments."""
        if name not in self._handlers:
            raise ValueError(f"Unknown tool: {name}")

        logger.debug("Executing tool '{}' with args: {}", name, arguments)
        return await self._handlers[name](**arguments)
