import pathlib

import aiofiles
from fastapi import Depends, File, HTTPException, Request, UploadFile, status, FastAPI, APIRouter

app = FastAPI()
router = APIRouter()
router2 = APIRouter()

class UploadedFile:
    file_id: int
    filename: str

    def __init__(self, filename):
        self.file_id = 123
        self.filename = filename


@router.post(
    "/api/v1/uploads",
    description="Uploads users upload to API",
    tags=["Files and storage"],
)
async def upload_files(request: Request, upload: UploadFile = File(...)):
    filename: str = upload.filename

    try:
        new_file = UploadedFile(filename)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"reason": "TOO_LONG_FILENAME", "message": "Filename is too long"}
        )

    media_location = pathlib.Path(__file__).parent / "media"
    file_root = media_location / str(new_file.file_id)
    file_root.mkdir()

    async with aiofiles.open((file_root / filename), mode="wb") as aio_f:
        await aio_f.write(upload.file.read())

    return {"file_id": new_file.file_id, "filename": new_file.filename}


if __name__ == "__main__":
    app.include_router(router)

    import uvicorn
    uvicorn.run(app)
