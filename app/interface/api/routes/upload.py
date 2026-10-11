from typing import Optional, AsyncIterator
import uuid
from fastapi import APIRouter, Depends, Form, UploadFile, File, Request
from app.domain.unit_of_work import AbstractUnitOfWork
from app.interface.api.dependencies import get_uow, get_current_user_id
from app.core.composition import get_file_ingestion_service, get_vector_store_service
from pathlib import Path
from app.interface.api.schemas.upload import UploadOutFileMetadata

router = APIRouter()


async def to_async_iterator(
    file: UploadFile, chunk_size: int = 1024 * 1024
) -> AsyncIterator[bytes]:
    await file.seek(0)
    while chunk := await file.read(chunk_size):
        yield chunk


@router.post("/upload", response_model=UploadOutFileMetadata)
async def upload(
    request: Request,
    file: UploadFile = File(...),
    notebook_id: Optional[uuid.UUID] = Form(None),
    user_id: uuid.UUID = Depends(get_current_user_id),
    uow: AbstractUnitOfWork = Depends(get_uow),
):
    stream = to_async_iterator(file)
    file_name = file.filename
    file_ext = Path(file.filename).suffix
    service = get_file_ingestion_service(
        uow, get_vector_store_service(vector_store=request.app.state.vector_store)
    )

    file_metadata = await service.upload_files(
        stream, file_name, file_ext, notebook_id, user_id
    )
    return file_metadata
