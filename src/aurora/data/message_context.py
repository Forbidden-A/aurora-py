"""Context of the current running turn."""

from hikari import Snowflakeish
from pydantic import BaseModel


class MessageContext(BaseModel):
    channel_id: Snowflakeish
    message_id: Snowflakeish
