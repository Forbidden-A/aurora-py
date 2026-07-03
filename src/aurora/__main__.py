"""Aurora main file."""

from __future__ import annotations
import sys

import logging
from loguru import logger

import hikari
import lightbulb

from aurora.config import Settings


class InterceptHandler(logging.Handler):
    """Routes standard logs to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Find the level of this log
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the origin of this log
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Actually output the log
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def build_bot(
    settings: Settings,
) -> tuple[hikari.GatewayBot, lightbulb.GatewayEnabledClient]:
    bot = hikari.GatewayBot(
        token=settings.discord_token,
        logs=None,
    )
    client = lightbulb.client_from_app(bot)
    bot.subscribe(hikari.StartingEvent, client.start)

    client.di.registry_for(lightbulb.di.Contexts.DEFAULT).register_value(
        Settings, settings
    )

    @bot.listen(hikari.StartedEvent)
    async def on_started(_: hikari.StartedEvent) -> None:
        me = bot.get_me()
        name = me.username if me is not None else "unknown"
        logger.info("Aurora is ready, logged in as {}", name)

    return bot, client


def main() -> None:
    settings = Settings()  # ty:ignore[missing-argument]
    logging.basicConfig(
        handlers=[InterceptHandler()], level=settings.general_log_level, force=True
    )
    logging.getLogger("aurora").setLevel(settings.log_level)
    bot, _client = build_bot(settings)
    bot.run()


if __name__ == "__main__":
    main()
