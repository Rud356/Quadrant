import os
import imghdr
from time import time
from app import app
from quart import send_file, request
from pathlib import Path
from bson import ObjectId
from bson import errors as bson_errors
from werkzeug.utils import secure_filename

from views import User
from models.file_model import FileModel
from .middlewares import authorized
from .responces import success, error

allowed_formats = {'gif', 'jpeg', 'png', 'webp'}
profile_pics_folder = Path(app.config['UPLOAD_FOLDER']) / 'profile_pics'
files_path = Path(app.config['UPLOAD_FOLDER'])


@app.route("/api/user/set_image", methods=["POST"])
@authorized
async def upload_profile_pic(user: User):
    if (
        request.content_length is None or
        request.content_length > 4 * 1024 * 1024
    ):
        return error("Too big file", 400)

    files = await request.files
    profile_img = files['file']

    if profile_img.filename == '':
        return error("None image selected", 400)

    if imghdr.what(profile_img) not in allowed_formats:
        return error("Incorrect file format", 400)

    profile_img.save(profile_pics_folder, user._id)
    return success("Profile image updated!")


@app.route("/api/user/<string:user_id>/profile_pic")
@authorized
async def get_profile_pic(user: User, user_id: str):
    try:
        user_id = ObjectId(ObjectId)
        user_id = str(user)
        if not os.path.isfile(profile_pics_folder / user_id):
            return error("No such pfp")

        filename = user_id + imghdr.what(profile_pics_folder / user_id)

        response = await send_file(profile_pics_folder / user_id)
        response.headers['x-filename'] = filename

        return response

    except bson_errors.InvalidId:
        return error("Invalid user id")


@app.route("/api/files/upload", methods=["POST"])
@authorized
async def upload_file(user: User):
    users_path = files_path / str(user._id)
    if not os.path.isdir(users_path):
        os.mkdir(users_path)

    files = await request.files
    regular_file = files['upload_files']

    if regular_file.filename == '':
        return error("None file selected", 400)

    system_filename = f"{int(time())}_{user._id}"
    with open(users_path / system_filename, 'wb') as f:
        regular_file.save(f)
    file_id = await user.create_file(
        secure_filename(regular_file.filename),
        system_filename
    )

    return success(f"/api/files/{file_id._id}")


@app.route("/api/files/<string:file_id>")
@authorized
async def get_file(user: User, file_id: str):
    try:
        file_id = ObjectId(file_id)
        file_info: FileModel = user.get_file(file_id)

        response = await send_file(file_info.systems_name)
        response.headers['x-filename'] = file_info.filename

        return response

    except bson_errors.InvalidId:
        return error("Invalid id")
