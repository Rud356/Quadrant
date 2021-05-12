import imghdr
from asyncio import get_event_loop
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image
from tornado.web import authenticated

from Quadrant.config import quadrant_config, casters
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper

MIN_IMAGE_SIZE = casters.file_size_caster("15k")
MAX_IMAGE_SIZE = casters.file_size_caster("4M")


class ProfilePictureUploadsHandler(QuadrantAPIHandler):
    profile_picture: Optional[bytes]

    @authenticated
    async def post(self):
        try:
            file = self.request.files['profile_picture']
            content = file['body']

        except KeyError:
            raise JsonHTTPError(status_code=400, reason="No file was uploaded")

        if len(content) not in range(MIN_IMAGE_SIZE, MAX_IMAGE_SIZE):
            raise JsonHTTPError(status_code=400, reason="Empty file uploaded")

        filetype = imghdr.what(None, h=content)
        if filetype not in {"jpeg", "png", "webp"}:
            raise JsonHTTPError(status_code=400, reason="Invalid file format")

        self.profile_picture = content
        self.write(JsonWrapper.dumps({"success": True}))

    @authenticated
    async def delete(self):
        base_path = quadrant_config.profile_pictures / str(self.user.id)
        (base_path / "image0.jpg").unlink(missing_ok=True)
        (base_path / "image0.webp").unlink(missing_ok=True)

        self.write(JsonWrapper.dumps({"success": True}))

    def thumbnail_image(self, profile_pictures_path: Path):
        """
        Saves image in webp and jpeg formats to save some traffic and space on drive.
        :param profile_pictures_path: path to pictures, saved on drive.
        :return: nothing.
        """
        with Image.open(BytesIO(self.profile_picture)) as img:
            img.thumbnail((1024, 1024))
            img.save(profile_pictures_path / "image0.jpg", "JPEG")
            img.save(profile_pictures_path / "image0.webp", "WEBP", method=3)

    async def on_finish(self) -> None:
        await super().on_finish()
        if self.profile_picture is not None:
            profile_pictures_path = quadrant_config.profile_pictures / str(self.user.id)
            get_event_loop().run_in_executor(None, self.thumbnail_image, profile_pictures_path)
