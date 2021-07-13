from pathlib import Path

import aiofiles
import pathvalidate
from fastapi import Depends, File, HTTPException, Request, UploadFile, status

from Quadrant.config import quadrant_config
from Quadrant.models import general
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import HTTPError, file_upload, UNAUTHORIZED_HTTPError, http_error_example
from .router import router


@router.post(
    "/api/v1/uploads",
    description="Uploads users upload to API",
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Files and storage"],
    responses={
        200: {"model": file_upload.FileUploadResponseSchema},
        status.HTTP_400_BAD_REQUEST: {"model": http_error_example("TOO_LONG_FILENAME", "Filename is too long")},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
    },
)
async def upload_files(request: Request, upload: UploadFile = File(...)):
    user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]
    filename: str = pathvalidate.sanitize_filename(upload.filename)

    try:
        new_file = await general.UploadedFile.create_file(user, filename, session=sql_session)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"reason": "TOO_LONG_FILENAME", "message": "Filename is too long"}
        )

    media_location: Path = quadrant_config.media_folder_location.value
    file_root = media_location / str(new_file.file_id)
    file_root.mkdir()

    async with aiofiles.open((file_root / filename), mode="wb") as aio_f:
        await aio_f.write(upload.file.read())

    return new_file.as_dict()
