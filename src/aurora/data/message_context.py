"""Context of the current running turn."""

from pydantic import BaseModel


class MessageContext(BaseModel):
    channel_id: int
    message_id: int
