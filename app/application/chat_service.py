from __future__ import annotations
from uuid import UUID
from app.application.ports.unit_of_work import AbstractUnitOfWork
from app.application.ports.rag.vector_store import AbstractVectorStore
from app.core.exceptions import InvalidCredentialsException
from app.schemas.message import Message, MessageRole, Citation
from app.application.workflow import LangGraphWorkflow
from app.application.schemas.chat_service import ChatResponse


class ChatService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        vector_store: AbstractVectorStore,
        workflow: LangGraphWorkflow,
    ):
        self._uow = uow
        self._vector_store = vector_store
        self._workflow = workflow

    async def chat(
        self,
        user_id: UUID,
        notebook_id: UUID,
        query: str,
    ) -> ChatResponse:
        async with self._uow:
            notebook = await self._uow.notebooks.get_notebook(notebook_id)
            if notebook is None:
                raise InvalidCredentialsException(
                    "Invalid Notebook Id",
                    details={
                        "user_id": str(user_id),
                        "notebook_id": str(notebook_id),
                    },
                )
            user_message = Message.create(MessageRole.USER, query, notebook_id, None)
            history_messages = await self._uow.messages.get_messages(notebook_id)
            retriever = self._vector_store.get_retriever(
                user_id=str(user_id), notebook_id=str(notebook_id)
            )
            response = await self._workflow.execute(
                history_messages + [user_message], retriever
            )
            citation_ref_ids = [
                Citation.create(doc["index"], doc["id"]) for doc in response["citation"]
            ]
            content = response["response"]
            assistant_message = Message.create(
                role=MessageRole.ASSISTANT,
                content=content,
                notebook_id=notebook_id,
                citation_refs=citation_ref_ids,
            )
            await self._uow.messages.save(user_message)
            await self._uow.messages.save(assistant_message)
            await self._uow.commit()
            return ChatResponse(
                assistant_message=assistant_message, citation=response["citation"]
            )
