import unittest
from uuid import UUID

from sqlalchemy import exc

from .datasets import async_session, create_user
from .utils import make_async_call


class TestUsersFunctionality(unittest.TestCase):
    @classmethod
    @make_async_call
    async def setUpClass(cls) -> None:
        cls.first_user_auth = await create_user("Rud_tester_1", "Rud_relationships", "IMakeRefsAdnIDontCare")
        cls.first_user = cls.first_user_auth.user
        cls.second_user_auth = await create_user("Rud_tester_2", "Rud_rel_2", "IDK_WTS_here")
        cls.first_user = cls.first_user_auth.user
