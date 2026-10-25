"""Module for conversation routers
contains chat router which is async without streaming"""

from uuid import UUID

from fastapi import APIRouter, Depends
from app.application.chat_service import ChatService
from app.interface.api.schemas.chat import ChatRequest, ChatRespose
from app.interface.api.dependencies import (
    get_chat_service,
    get_current_user_id,
)
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatRespose,
    summary="Ask a question about the documents in a session",
    responses={
        404: {
            "description": "notebook_id does not exist or does not belong to the current user"
        },
        503: {"description": "The LLM provider failed or timed out after retries"},
    },
)
async def chat(
    payload: ChatRequest,
    user_id: UUID = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatRespose:
    """
    Runs the RAG pipeline: retrieves the top-k relevant chunks from the
    session's documents, then generates an answer that cites its sources
    as `[1]`, `[2]`, etc. `top_k_docs` in the response lists the chunks used.
    """

    notebook_id = payload.notebook_id
    query = payload.query
    response = await chat_service.chat(
        user_id, notebook_id, query
    )
    return ChatRespose(
        query=payload.query,
        response=response.assistant_message.content,
        citation=response.citation,
    )