"""Aurora main file."""

from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime
from types import FrameType

import hikari
import lightbulb
import linkd
from loguru import logger

from aurora.actions import ActionManager, register_discord_actions
from aurora.agent import run_turn
from aurora.config import Settings
from aurora.data.message_context import MessageContext
from aurora.di import Contexts
from aurora.llm import LLMClient
from aurora.tools import ToolRegistry


class InterceptHandler(logging.Handler):
    """Routes standard logs to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Find the level of this log
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the origin of this log
        frame: FrameType | None
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Actually output the log
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def build_bot(
    settings: Settings,
) -> tuple[hikari.GatewayBot, lightbulb.GatewayEnabledClient]:
    hikari_bot = hikari.GatewayBot(
        token=settings.discord_token,
        intents=hikari.Intents.ALL_GUILDS_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
        logs=None,
    )
    lightbulb_client = lightbulb.client_from_app(hikari_bot)
    hikari_bot.subscribe(hikari.StartingEvent, lightbulb_client.start)

    action_manager = ActionManager()
    register_discord_actions(action_manager)

    llm_client = LLMClient(
        model=settings.model_name,
        base_url=settings.model_base_url,
        api_key=settings.model_api_key,
    )

    tool_registry = ToolRegistry()
    di_manager = lightbulb_client.di
    default_registry = di_manager.registry_for(linkd.Contexts.ROOT)
    default_registry.register_value(Settings, settings)
    default_registry.register_value(ActionManager, action_manager)
    default_registry.register_value(LLMClient, llm_client)
    default_registry.register_value(ToolRegistry, tool_registry)
    default_registry.register_value(hikari.api.RESTClient, hikari_bot.rest)  # type: ignore[type-abstract]

    @hikari_bot.listen(hikari.StartedEvent)
    async def on_started(_: hikari.StartedEvent) -> None:  # noqa: RUF029
        me = hikari_bot.get_me()
        name = me.username if me is not None else "unknown"
        logger.info("Aurora is ready, logged in as {}", name)

    @hikari_bot.listen(hikari.GuildMessageCreateEvent)
    async def on_guild_message_create(event: hikari.GuildMessageCreateEvent) -> None:
        logger.debug(
            "Recieved GuildMessageCreateEvent: {}: {}", event.author_id, event.message.content
        )

        if not event.is_human or not event.content:
            if not event.is_human:
                logger.debug("It is not a human-sent message.")
            if not event.content:
                logger.debug("The content is falsey: {}", event.content)
            return

        message_context = MessageContext(channel_id=event.channel_id, message_id=event.message_id)

        realtime_context = (
            f"Current UTC time: {datetime.now(tz=UTC).isoformat()}"
            # TODO: Give agent a channel view for the whole guild.
        )

        async with (
            di_manager.enter_context(linkd.Contexts.ROOT),
            di_manager.enter_context(Contexts.MESSAGE) as message_container,
        ):
            message_container.add_value(MessageContext, message_context)
            try:
                await run_turn(
                    llm=llm_client,
                    actions=action_manager,
                    tools=tool_registry,
                    user_content=event.content,
                    realtime_context=realtime_context,
                )
            except Exception as e:
                logger.exception(
                    "Unhandled error while processing message in channel {}: {}",
                    event.channel_id,
                    e,
                )

    return hikari_bot, lightbulb_client


def main() -> None:
    settings = Settings()  # ty:ignore[missing-argument] (fields load from the environment)
    logging.basicConfig(handlers=[InterceptHandler()], level=settings.general_log_level, force=True)
    logging.getLogger("aurora").setLevel(settings.log_level)
    bot, _client = build_bot(settings)
    bot.run()


if __name__ == "__main__":
    main()
