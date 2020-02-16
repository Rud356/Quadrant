from collections import namedtuple

auth_data = namedtuple("Authorization_data", ["login", "password"])
auth_token = namedtuple("Token_auth", ["token"])