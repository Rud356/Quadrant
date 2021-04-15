from random import randint
from secrets import token_urlsafe


def generate_random_color() -> int:
    """
    Generates a random color integer
    :return: color integer that can be used in ui or be shown as unique part of nickname to separate users_package
    """
    return randint(0x000000, 0xFFFFFF)


def generate_internal_token() -> str:
    return token_urlsafe(randint(72, 96))
