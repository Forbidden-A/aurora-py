"""Helpers for building and formatting LLM messages and prompts."""

from __future__ import annotations

import json
from pathlib import Path

from openai.types.chat import ChatCompletionMessageParam

RESOURCES_DIR = Path(__file__).parent.parent.parent.parent / "resources"


def load_persona() -> str:
    """Load and serialize the persona JSON."""
    with open(RESOURCES_DIR / "persona.json", encoding="utf-8") as f:
        return json.dumps(json.load(f), indent=2)


def load_examples() -> str:
    """Load the examples markdown file."""
    with open(RESOURCES_DIR / "examples.md", encoding="utf-8") as f:
        return f.read()


def format_system_prompt(actions: str, realtime_context: str) -> str:
    """
    Format the system.md template with the persona, examples, and available actions.
    """
    system_template = (RESOURCES_DIR / "system.md").read_text(encoding="utf-8")

    return system_template.format(
        actions=actions,
        persona=load_persona(),
        realtime=realtime_context,
        examples=load_examples(),
    )


def build_initial_messages(
    system_prompt: str, user_content: str
) -> list[ChatCompletionMessageParam]:
    """Create the initial message list for a new agent turn."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
