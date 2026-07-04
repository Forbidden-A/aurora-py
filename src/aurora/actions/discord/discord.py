"""Discord action registration"""

import typing

from aurora.actions.discord.basic import register_basic_actions

if typing.TYPE_CHECKING:
    from aurora.actions.manager import ActionManager


def register_discord_actions(manager: ActionManager) -> None:
    register_basic_actions(manager)
