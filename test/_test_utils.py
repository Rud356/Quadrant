from random import choices
from string import ascii_letters, digits

from app import client
from models import user_model

charset = digits + ascii_letters


def rand_string(length=25):
    return ''.join(choices(charset, k=length))


async def create_user() -> (str, str):
    login = rand_string(50)
    password = rand_string(120)

    await user_model.UserModel.registrate(
        rand_string(), login, password
    )

    return login, password


async def drop_db():
    await client.drop_database("debug_chat")
