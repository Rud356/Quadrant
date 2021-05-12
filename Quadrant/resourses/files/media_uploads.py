from tornado.web import Finish, authenticated

from Quadrant.config import quadrant_config
from Quadrant.models import general
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class MediaUploadsHandler(QuadrantAPIHandler):
    @authenticated
    async def post(self):
        try:
            file = self.request.files['file']
            filename = file['filename']
            content = file['body']

        except KeyError:
            raise JsonHTTPError(status_code=400, reason="No file was uploaded")

        if len(content) < 1:
            raise JsonHTTPError(status_code=400, reason="Empty file uploaded")

        try:
            new_file = await general.File.create_file(self.user, filename, session=self.session)

        except ValueError:
            raise JsonHTTPError(status_code=400, reason="Invalid filename")

        # TODO: maybe make this optionally able to upload files anywhere else
        base_dir = quadrant_config.uploads
        file_base_dir = base_dir / str(new_file.file_id)
        file_base_dir.mkdir()
        (file_base_dir / new_file.filename).write_bytes(content)

        self.write(JsonWrapper.dumps({"file_id": new_file.file_id}))
        raise Finish()
