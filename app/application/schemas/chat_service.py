from dataclasses import dataclass
from app.schemas.message import Message


@dataclass
class ChatResponse:
    assistant_message: Message
    citation: list[dict]
