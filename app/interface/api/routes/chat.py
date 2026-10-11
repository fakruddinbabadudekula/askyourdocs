"""Module for conversation routers
contains chat router which is async without streaming"""

from uuid import UUID

from fastapi import APIRouter, Depends
from app.application.notebook_chat_service import NotebookChatService
from app.interface.api.schemas.chat import ChatRequest, ChatRespose
from app.interface.api.dependencies import (
    get_container,
    get_current_user_id,
    get_notebook_service,
)
from app.root import Container

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
    notebook_chat_service: NotebookChatService = Depends(get_notebook_service),
    container: Container = Depends(get_container),
) -> ChatRespose:
    """
    Runs the RAG pipeline: retrieves the top-k relevant chunks from the
    session's documents, then generates an answer that cites its sources
    as `[1]`, `[2]`, etc. `top_k_docs` in the response lists the chunks used.
    """

    notebook_id = payload.notebook_id
    retriever_filter = container.get_retriever_filter(user_id, notebook_id)
    query = payload.query
    response = await notebook_chat_service.chat(
        user_id, notebook_id, query, retriever_filter
    )
    return ChatRespose(
        query=payload.query,
        response=response["assistant_message"].content,
        top_k_context=response["top_k_context"],
    )
