from typing import Optional, AsyncIterator
import uuid
from fastapi import APIRouter, Depends, Form, UploadFile, File
from app.application.file_ingestion_service import FileIngestionService
from app.interface.api.dependencies import (
    get_current_user_id,
    get_file_ingestion_service,
)
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
    file: UploadFile = File(...),
    notebook_id: Optional[uuid.UUID] = Form(None),
    user_id: uuid.UUID = Depends(get_current_user_id),
    file_ingestion_service: FileIngestionService = Depends(get_file_ingestion_service),
):
    stream = to_async_iterator(file)
    file_name = file.filename
    file_ext = Path(file.filename).suffix
    file_metadata = await file_ingestion_service.upload_files(
        stream, file_name, file_ext, notebook_id, user_id
    )
    return file_metadata
