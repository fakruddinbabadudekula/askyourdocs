from app.schemas.user import User
from app.schemas.message import Message, Citation
from app.schemas.file_metadata import FileMetadata
from app.schemas.document_ref import DocumentRef
from app.schemas.notebook import Notebook
from app.schemas.refresh_token import RefreshToken
from app.infrastructure.sqlalchemy_repositories.models.user import User as OrmUser
from app.infrastructure.sqlalchemy_repositories.models.refresh_token import (
    RefreshToken as OrmRefreshToken,
)
from app.infrastructure.sqlalchemy_repositories.models.notebook import (
    Notebook as OrmNotebook,
)
from app.infrastructure.sqlalchemy_repositories.models.file import (
    FileMetadata as OrmFileMetadata,
)
from app.infrastructure.sqlalchemy_repositories.models.message import (
    Message as OrmMessage,
)
from app.infrastructure.sqlalchemy_repositories.models.document_ref import (
    DocumentRef as OrmDocumentRef,
)


def orm_to_user(orm: OrmUser) -> User:
    user = User(
        name=orm.name,
        email=orm.email,
        hashed_password=orm.hashed_password,
        user_id=orm.user_id,
        created_at=orm.created_at,
    )
    return user


def user_to_orm(user: User) -> OrmUser:
    return OrmUser(
        name=user.name,
        email=user.email,
        hashed_password=user.hashed_password,
        user_id=user.user_id,
        created_at=user.created_at,
    )


def refresh_token_to_orm(token: RefreshToken) -> OrmRefreshToken:
    return OrmRefreshToken(
        token_id=token.token_id,
        hashed_token=token.hashed_token,
        status=token.status,
        user_id=token.user_id,
        created_at=token.created_at,
        family_id=token.family_id,
        expires_at=token.expires_at,
        revoked_at=token.revoked_at,
    )


def orm_to_refresh_token(orm: OrmRefreshToken) -> RefreshToken:
    token = RefreshToken(
        token_id=orm.token_id,
        hashed_token=orm.hashed_token,
        status=orm.status,
        user_id=orm.user_id,
        created_at=orm.created_at,
        family_id=orm.family_id,
        expires_at=orm.expires_at,
        revoked_at=orm.revoked_at,
    )
    return token


def notebook_to_orm(notebook: Notebook) -> OrmNotebook:
    return OrmNotebook(
        notebook_id=notebook.notebook_id,
        title=notebook.title,
        user_id=notebook.user_id,
        created_at=notebook.created_at,
    )


def orm_to_notebook(
    notebook_orm: OrmNotebook,
) -> Notebook:
    return Notebook(
        notebook_id=notebook_orm.notebook_id,
        title=notebook_orm.title,
        user_id=notebook_orm.user_id,
        created_at=notebook_orm.created_at,
    )


def message_to_orm(message: Message) -> OrmMessage:
    return OrmMessage(
        message_id=message.message_id,
        notebook_id=message.notebook_id,
        content=message.content,
        role=message.role,
        citation_refs=(
            [docs.as_dict() for docs in message.citation_refs]
            if message.citation_refs
            else None
        ),
        created_at=message.created_at,
    )


def orm_to_message(orm: OrmMessage) -> Message:
    return Message(
        message_id=orm.message_id,
        notebook_id=orm.notebook_id,
        content=orm.content,
        role=orm.role,
        citation_refs=(
            [
                Citation.create(doc["index"], doc["id"])
                for doc in orm.citation_refs
            ]
            if orm.citation_refs
            else None
        ),
        created_at=orm.created_at,
    )


def file_to_orm(file: FileMetadata) -> OrmFileMetadata:
    return OrmFileMetadata(
        file_id=file.file_id,
        notebook_id=file.notebook_id,
        type=file.type,
        name=file.name,
        size=file.size,
        created_at=file.created_at,
    )


def orm_to_file(orm: OrmFileMetadata) -> FileMetadata:
    return FileMetadata(
        file_id=orm.file_id,
        notebook_id=orm.notebook_id,
        type=orm.type,
        name=orm.name,
        size=orm.size,
        created_at=orm.created_at,
    )


def orm_to_document_ref(orm: OrmDocumentRef) -> DocumentRef:
    return DocumentRef(doc_id=orm.doc_id, file_id=orm.file_id)


def document_ref_to_orm(doc_ref: DocumentRef) -> OrmDocumentRef:
    return OrmDocumentRef(doc_id=doc_ref.doc_id, file_id=doc_ref.file_id)
