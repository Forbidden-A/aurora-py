"""Provider-agnostic LLM client wrapper using the OpenAI SDK."""

from __future__ import annotations
import typing

import os
from openai import AsyncOpenAI, Omit
from loguru import logger

if typing.TYPE_CHECKING:
    from openai.types.chat import (
        ChatCompletion,
        ChatCompletionMessageParam,
        ChatCompletionFunctionToolParam,
        ChatCompletionCustomToolParam,
    )


class LLMClient:
    """Wraps AsyncOpenAI to support Ollama (and other OpenAI-compatible APIs)."""

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model = model

        self.client = AsyncOpenAI(
            base_url=base_url
            or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key=api_key or os.getenv("OLLAMA_API_KEY", "ollama"),
        )

    async def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        tools: list[ChatCompletionFunctionToolParam | ChatCompletionCustomToolParam]
        | Omit = Omit(),
    ) -> ChatCompletion:
        """Send a chat completion request to the LLM."""
        logger.debug(
            "Calling LLM '{}' with {} messages and {} tools",
            self.model,
            len(messages),
            len(tools) if tools else 0,
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
        )

        return response
