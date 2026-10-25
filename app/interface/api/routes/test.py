from uuid import UUID
from fastapi import APIRouter, Depends
from app.interface.api.dependencies import get_current_user_id

router = APIRouter()


@router.get("/test/current_user")
def get_user(user_id: UUID = Depends(get_current_user_id)):
    return user_id
