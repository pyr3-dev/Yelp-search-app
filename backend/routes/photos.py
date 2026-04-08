from fastapi import APIRouter
from fastapi.responses import FileResponse

from controllers.photos import serve_photo_controller

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{photo_id}", response_class=FileResponse)
async def serve_photo(photo_id: str) -> FileResponse:
    return await serve_photo_controller(photo_id=photo_id)
