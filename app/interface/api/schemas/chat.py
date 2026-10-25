"""Module for schemas which are specific for chat request"""

from pydantic import BaseModel
import uuid


class ChatRequest(BaseModel):
    notebook_id: uuid.UUID
    query: str


class ChatRespose(BaseModel):
    query: str
    response: str
    citation: list[dict]