import unittest

from sqlalchemy import exc

from Quadrant.migrations import db_utils
from Quadrant.models import users_package
from Quadrant.models.db_init import async_session
from tests.datasets import create_user
from tests.utils import clean_tests_folders, make_async_call


class TestUserInDBCreation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        db_utils.initialize_db()

    @make_async_call
    @async_session
    async def test_register_user_internally(self, session):
        user = await create_user("Rud tester", login="Rud356", password="example_password_123A", session=session)
        self.assertIsInstance(user, users_package.user_auth.UserInternalAuthorization)

    @make_async_call
    @async_session
    async def test_register_duplicate_user_internally(self, session):
        with self.assertRaises(exc.IntegrityError):
            await create_user("Rud tester", login="Rud356.2", password="example_password_123Ax", session=session)
            await create_user("Rud tester 2", login="Rud356.2", password="example_password_123Ax", session=session)

    @classmethod
    def tearDownClass(cls) -> None:
        db_utils.drop_db()
        clean_tests_folders()
