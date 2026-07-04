"""Manages action registration, parsing, and execution."""

from __future__ import annotations
import typing
from pydantic import BaseModel, Field

import re
from loguru import logger

if typing.TYPE_CHECKING:
    from typing import Callable, Awaitable


class ActionEntry(BaseModel):
    """Represents a registered action."""

    name: str
    description: str
    field_name: str | None = Field(
        description="The name of the parameter in the action.", default=None
    )
    handler: Callable[..., Awaitable[str]] = Field(
        description="The function to execute."
    )

    def get_syntax(self) -> str:
        """Return the action syntax for the system prompt."""
        if self.field_name:
            return f"`[{self.name.upper()}:<{self.field_name}>]` - {self.description}"
        return f"``[{self.name.upper()}]` - {self.description}"


class ActionManager:
    """Parses and executes actions from model output."""

    # Pattern match actions `[ACTION:VALUE]` or `[ACTION]` (and `[ACTION: VALUE]`)
    ACTION_PATTERN = re.compile(r"\[(\w+)(?::\s*(.+?))?\]")

    def __init__(self) -> None:
        self._actions: dict[str, ActionEntry] = {}

    def register(self, action: ActionEntry) -> None:
        """Register an action."""
        self._actions[action.name.casefold()] = action
        logger.debug("Registered action: {}", action.name)

    def get_actions_prompt(self) -> str:
        """Generate the actions section for the system prompt."""
        if not self._actions:
            return "No actions available."

        actions_list = "\n".join(
            f"- {action.get_syntax()}" for action in self._actions.values()
        )
        return f"{actions_list}"

    def parse_actions(self, text: str) -> list[tuple[str, str | None]]:
        """
        Parse actions from text.
        Returns list of (action_name, value) tuples.
        """
        return self.ACTION_PATTERN.findall(text)

    async def execute_action(
        self,
        name: str,
        value: str | None,
    ) -> str:
        """Execute an action by name."""
        action = self._actions.get(name.casefold())
        if not action:
            raise ValueError(f"Unknown action: {name}")

        logger.debug("Executing action '{}' with value: {}", name, value)

        if action.field_name and not value:
            logger.error(
                "Failed to execute action '{}', '{}' was not provided.",
                name,
                action.field_name,
            )
            raise ValueError(
                f"Action '{name}' requires '{action.field_name}' but it was not provided"
            )

        return await action.handler(value)

    def has_action(self, name: str) -> bool:
        """Check if an action is registered."""
        return name.casefold() in self._actions
