import unittest
from uuid import UUID

from sqlalchemy import exc

from Quadrant.models.db_init import Session
from .datasets import create_user, async_init_db, async_drop_db
from .utils import clean_tests_folders, make_async_call


class TestUsersFunctionality(unittest.TestCase):
    @classmethod
    @make_async_call
    async def setUpClass(cls) -> None:
        cls.session = Session()
        await async_drop_db()
        await async_init_db()

        cls.first_user_auth = await create_user("Rud_tester_1", "Rud_relationships", "IMakeRefsAdnIDontCare")
        cls.first_user = cls.first_user_auth.user
        cls.second_user_auth = await create_user("Rud_tester_2", "Rud_rel_2", "IDK_WTS_here")
        cls.first_user = cls.first_user_auth.user

    @classmethod
    @make_async_call
    async def tearDownClass(cls) -> None:
        clean_tests_folders()
        await async_drop_db()
        await cls.session.close()  # noqa: setted in setUpClass
