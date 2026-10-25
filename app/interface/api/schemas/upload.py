from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.domain.file_metadata import FileType
from datetime import datetime


class UploadOutFileMetadata(BaseModel):
    file_id: UUID
    notebook_id: UUID
    type: FileType
    name: str
    size: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
