"""Basic Discord actions."""

from __future__ import annotations

import typing

import hikari
import linkd
from loguru import logger

from aurora.actions.manager import ActionEntry
from aurora.data import MessageContext

if typing.TYPE_CHECKING:
    from aurora.actions.manager import ActionManager


@linkd.inject
async def note_action(
    value: str,
    message_context: MessageContext = linkd.INJECTED,
    rest: hikari.api.RESTClient = linkd.INJECTED,
) -> str:
    """Handle NOTE action. Temporarily always sends the notes."""
    logger.debug("[NOTE] (channel={}, message={}) {}", message_context.channel_id, value)
    # TODO: Check whether notes are enabled before sending the message.
    try:
        await rest.create_message(
            channel=message_context.channel_id,
            content=f">>> {value}",
            reply=message_context.message_id,
            mentions_reply=False,
            mentions_everyone=False,
            user_mentions=False,
            role_mentions=False,
        )
        return "SUCCESS"
    except Exception:
        return "FAILURE"


@linkd.inject
async def send_action(
    value: str,
    message_context: MessageContext = linkd.INJECTED,
    rest: hikari.api.RESTClient = linkd.INJECTED,
) -> str:
    """Handle SEND action."""
    logger.debug(
        "[SEND] (channel={}, message={}) {}",
        message_context.channel_id,
        message_context.message_id,
        value,
    )

    try:
        await rest.create_message(
            channel=message_context.channel_id,
            content=value,
            reply=message_context.message_id,
            mentions_reply=False,
            mentions_everyone=False,
            user_mentions=False,
            role_mentions=False,
        )
        return "SUCCESS"
    except Exception:
        return "FAILURE"


@linkd.inject
async def add_reaction_action(
    value: str,
    message_context: MessageContext = linkd.INJECTED,
    rest: hikari.api.RESTClient = linkd.INJECTED,
) -> str:
    """Handle ADD_REACTION action."""
    logger.debug(
        "[ADD_REACTION] (channel={}, message={}) {}",
        message_context.channel_id,
        message_context.message_id,
        value,
    )
    try:
        await rest.add_reaction(message_context.channel_id, message_context.message_id, value)
        return "SUCCESS"
    except Exception:
        return "FAILURE"


def register_basic_actions(
    manager: ActionManager,
) -> None:
    """Register all Discord actions."""
    manager.register(
        ActionEntry(
            name="note",
            field_name="thoughts",
            handler=note_action,
            description=(
                "Internal note for reasoning. Use this to think before acting."
                " Must be used before any other action."
            ),
        )
    )

    manager.register(
        ActionEntry(
            name="send",
            field_name="message_content",
            handler=send_action,
            description=(
                "Send a message reply to the user. If this action is NOT used, the user will"
                " not see your response."
            ),
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
