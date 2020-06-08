import imghdr
import os
from pathlib import Path
from random import choices
from string import ascii_letters
from time import time

from bson import ObjectId
from bson import errors as bson_errors
from quart import request, send_file
from werkzeug.utils import secure_filename

from app import app
from models.enums import UpdateType
from models.message_model import UpdateMessage
from models.file_model import FileModel
from user_view import User

from .middlewares import authorized
from .responces import error, success

allowed_formats = {'gif', 'jpeg', 'png', 'webp'}
profile_pics_folder = Path(app.config['UPLOAD_FOLDER']) / 'profile_pics'
files_path = Path(app.config['UPLOAD_FOLDER'])


@authorized
async def upload_profile_pic(user: User):
    """
    Payload: file ["image"]  
    Limits: 4MB file of gif, jpeg, png, webp formats  
    Response codes: 200, 400, 401
    """

    if (
        request.content_length is None or
        request.content_length > 4 * 1024 * 1024
    ):
        return error("Too big file", 400)

    files = await request.files
    profile_img = files['image']

    if profile_img.filename == '':
        return error("None image selected", 400)

    if imghdr.what(profile_img) not in allowed_formats:
        return error("Incorrect file format", 400)

    with open(profile_pics_folder / user._id, "wb") as f:
        profile_img.save(f)

    update_message = UpdateMessage(
        {
            "user_id": user._id,
        },
        UpdateType.image_updated
    )
    await user.broadcast_to_friends(update_message)
    return success("Profile image updated!")


@authorized
async def get_profile_pic(user: User, user_id: str):
    """
    Requires: user_id in route  
    Response: 404, file
    """

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


@authorized
async def upload_file(user: User):
    """
    Requires: files  
    Response: list of files names
    """

    files = await request.files
    files_ids = []

    for file_name in files:
        file = files[file_name]
        if file.filename == '':
            continue

        rand_part = ''.join(choices(ascii_letters, k=12))

        system_file_name = f"{time()}_{user._id}_{rand_part}"
        with open(files_path / system_file_name, 'wb') as f:
            file.save(f)

            await FileModel.create_file(
                secure_filename(file.filename),
                system_file_name
            )

        files_ids.append(system_file_name)

    return success(files_ids)


@authorized
async def get_file(user: User, file_name: str):
    """
    Requires: file name in route  
    Response: 404, file
    """

    try:
        file_name = files_path / file_name

        with open(file_name, 'rb') as f:
            response = await send_file(f)

        file_record = FileModel.get_file(file_name)
        response.headers['x-filename'] = file_record.file_name

        return response

    except FileNotFoundError:
        return error("Invalid file")
