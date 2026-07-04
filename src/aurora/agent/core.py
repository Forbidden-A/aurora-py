"""The agent turn orchestrator, builds the prompt, calls the LLM, executes actions."""

from __future__ import annotations

import typing

from loguru import logger
from openai import Omit

from aurora.llm import build_initial_messages, format_system_prompt

if typing.TYPE_CHECKING:
    from aurora.actions import ActionManager
    from aurora.llm import LLMClient
    from aurora.tools import ToolRegistry

_DEFAULT_OMIT = Omit()


async def run_turn(
    llm: LLMClient,
    actions: ActionManager,
    tools: ToolRegistry,
    user_content: str,
    realtime_context: str,
) -> None:
    """Runs one agent turn: prompt -> completion -> parse actions -> execute them."""
    system_prompt = format_system_prompt(actions.get_actions_prompt(), realtime_context)
    messages = build_initial_messages(system_prompt, user_content)

    response = await llm.complete(messages, tools=tools.get_tools() or _DEFAULT_OMIT)
    text = response.choices[0].message.content or ""

    if not text.strip():
        logger.debug("Model returned no text content for this turn")
        return

    parsed = actions.parse_actions(text)
    if not parsed:
        logger.debug("Model responded without using any action: {}", text)
        return

    for name, value in parsed:
        if not actions.has_action(name):
            logger.warning("Model tried to use unknown action: '{}'", name)
            continue

        try:
            await actions.execute_action(name, value)
        except Exception:
            logger.error("Action '{}' failed to execute")
