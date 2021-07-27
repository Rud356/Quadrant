from pathlib import Path

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import Depends, File, HTTPException, Request, UploadFile, status

from PIL import Image, UnidentifiedImageError
from Quadrant.models import users_package
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import file_upload, UNAUTHORIZED_HTTPError, http_error_example
from .router import router

thread_executor = ThreadPoolExecutor(50, thread_name_prefix="Image_processing")


def create_thumbnails(file_root: Path, file: UploadFile):
    with Image.open(file.file) as img:
        img.thumbnail((1024, 1024))
        img.save(file_root / "image.jpeg", "JPEG")
        img.save(file_root / "image.webp", "webp")


@router.post(
    "/api/v1/profile/profile_picture",
    description="""
    Updates profile picture for user.
    To fetch user profile images you have to use route
    /media/profile_pictures/{user_id}/image.jpeg or image.webp
    """,
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["User profile management", "Files and storage"],
    responses={
        200: {"model": file_upload.UserProfilePictureUpdated},
        status.HTTP_400_BAD_REQUEST: {"model": http_error_example("INVALID_FILE_FORMAT", "File isn't valid image")},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
    },
)
async def upload_files(request: Request, upload: UploadFile = File(...)):
    user: users_package.User = request.scope["db_user"]
    loop = asyncio.get_running_loop()

    try:
        await loop.run_in_executor(
            thread_executor, create_thumbnails, user.profile_picture_path, upload
        )

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"reason": "INVALID_FILE_FORMAT", "message": "File isn't valid image"}
        )

    return {"updated_image": True}
