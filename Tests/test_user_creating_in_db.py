import unittest

from sqlalchemy import exc

from Quadrant.models import users_package
from .datasets import create_user
from .utils import make_async_call


class TestUserInDBCreation(unittest.TestCase):
    @make_async_call
    async def test_register_user_internally(self):
        user = await create_user("Rud tester", login="Rud356", password="example_password_123A")
        self.assertIsInstance(user, users_package.user_auth.UserInternalAuthorization)

    @make_async_call
    async def test_register_duplicate_user_internally(self):
        with self.assertRaises(exc.IntegrityError):
            await create_user("Rud tester", login="Rud356.2", password="example_password_123Ax")
            await create_user("Rud tester 2", login="Rud356.2", password="example_password_123Ax")
