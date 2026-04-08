from fastapi import HTTPException
from fastapi.responses import FileResponse

from services.photos import get_photo_path


async def serve_photo_controller(photo_id: str) -> FileResponse:
    path = get_photo_path(photo_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(path, media_type="image/jpeg")
