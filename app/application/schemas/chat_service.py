from dataclasses import dataclass
from app.domain.message import Message


@dataclass
class ChatResponse:
    assistant_message: Message
    citation: list[dict]
