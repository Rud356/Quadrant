from functools import partial
from hashlib import sha256, pbkdf2_hmac
from os import urandom
from random import randint, choices
from string import ascii_letters, digits
from time import time

from app.app import loop

CHARSET = ascii_letters + digits
EXCLUDE_PUBLIC = {
    "friend_code": 0, "salt": 0, "password": 0,
    "token": 0, "login": 0, "status": 0, "friends": 0, "blocked": 0,
    "incoming_friend_requests": 0, "outgoing_friend_requests": 0
}
EXCLUDE_LOADING = {
    "friends": 0, "blocked": 0,
    "incoming_friend_requests": 0, "outgoing_friend_requests": 0
}

run_async = partial(loop.run_in_executor, None)


def generate_salt(size=64) -> str:
    return sha256(urandom(size)).hexdigest()


def generate_token() -> str:
    return hex(round(time())) + ''.join(
        choices(CHARSET, k=randint(50, 72))
    )


async def calculate_password_hash(password: str, salt: str):
    @run_async
    def hash_calculation():
        return pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000
        ).hex()

    return await hash_calculation()
