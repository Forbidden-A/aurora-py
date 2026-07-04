"""Basic Discord actions."""

from __future__ import annotations
import typing

from loguru import logger
from aurora.actions.manager import ActionEntry

if typing.TYPE_CHECKING:
    from aurora.actions.manager import ActionManager


async def note_action(value: str) -> str:
    """Handle NOTE action. Temporarily logged only."""
    logger.debug("[NOTE] {}", value)
    return "SUCCESS"


async def send_action(value: str) -> str:
    """Handle SEND action. Temporarily logged only."""

    logger.debug("[SEND] {}", value)
    return "SUCCESS"


async def add_reaction_action(value: str) -> str:
    """Handle ADD_REACTION action. Temporarily logged only."""

    logger.debug("[ADD_REACTION] {}", value)
    return "SUCCESS"


def register_basic_actions(
    manager: ActionManager,
) -> None:
    """Register all Discord actions."""
    manager.register(
        ActionEntry(
            name="note",
            field_name="thoughts",
            handler=note_action,
            description="Internal note for reasoning. Use this to think before acting. Must be used before any other action.",
        )
    )

    manager.register(
        ActionEntry(
            name="send",
            field_name="message_content",
            handler=send_action,
            description="Send a message reply to the user. If this action is NOT used, the user will not see your response.",
        )
    )

    manager.register(
        ActionEntry(
            name="react",
            field_name="emoji",
            handler=add_reaction_action,
            description="Reacts to a user's message with the provided emoji.",
        )
    )
