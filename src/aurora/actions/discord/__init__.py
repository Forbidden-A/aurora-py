"""Discord-specific actions."""

from aurora.actions.manager import ActionManager

from aurora.actions.discord.basic import register_basic_actions


def register_discord_actions(manager: ActionManager):
    register_basic_actions(manager)


__all__ = ["register_discord_actions"]
