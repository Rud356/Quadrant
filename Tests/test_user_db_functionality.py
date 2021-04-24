import unittest
from uuid import UUID

from sqlalchemy import exc

from Quadrant.models.utils.common_settings_validators import DEFAULT_COMMON_SETTINGS_DICT
from .datasets import async_session, create_user
from .utils import make_async_call


class TestUsersFunctionality(unittest.TestCase):
    @classmethod
    @make_async_call
    async def setUpClass(cls) -> None:
        cls.test_user_auth = await create_user("Rud_func", "Rud_functions_tester", "H0w_h4rd_lma0")
        cls.test_user = cls.test_user_auth.user

    @make_async_call
    @async_session
    async def test_getting_user(self, session):
        got_user = await self.test_user.get_user(self.test_user.id, session=session)
        self.assertEqual(got_user, self.test_user, f"Somehow user with id {self.test_user.id} didn't got himself")

    @make_async_call
    @async_session
    async def test_getting_not_existing_user(self, session):
        not_existing_user_id = UUID('683a2e17-934a-42e0-852d-e642ddcf2863')

        with self.assertRaises(exc.NoResultFound):
            await self.test_user.get_user(not_existing_user_id, session=session)

    @make_async_call
    @async_session
    async def test_setting_text_status(self, session):
        new_text_status = "Hello world"
        await self.test_user.set_text_status(new_text_status, session=session)
        got_user = await self.test_user.get_user(self.test_user.id, session=session)

        self.assertEqual(got_user.text_status, self.test_user.text_status)

    @make_async_call
    @async_session
    async def test_setting_null_text_status(self, session):
        new_text_status = None

        with self.assertRaises(exc.IntegrityError):
            await self.test_user.set_text_status(
                new_text_status, session=session  # noqa: testing that it doesn't works
            )

    @make_async_call
    @async_session
    async def test_setting_status(self, session):
        await self.test_user.set_status("offline", session=session)
        got_user = await self.test_user.get_user(self.test_user.id, session=session)

        self.assertEqual(got_user.status, self.test_user.status)

    @make_async_call
    @async_session
    async def test_setting_invalid_status(self, session):
        with self.assertRaises(KeyError):
            await self.test_user.set_status("IDK what i am", session=session)

    @make_async_call
    @async_session
    async def test_setting_username(self, session):
        await self.test_user.set_username("Hello there", session=session)
        got_user = await self.test_user.get_user(self.test_user.id, session=session)

        self.assertEqual(got_user.username, self.test_user.username)

    def test_users_default_settings_matching_defaults(self):
        self.assertDictEqual(
            self.test_user.users_common_settings.common_settings,
            DEFAULT_COMMON_SETTINGS_DICT
        )

    @make_async_call
    @async_session
    async def test_updating_settings(self, session):
        fields_was_updated = await self.test_user.users_common_settings.update_settings(
            settings={"enable_sites_preview": True}, session=session
        )
        self.assertEqual(fields_was_updated['updated_fields'], ("enable_sites_preview",))
        self.assertTrue(self.test_user.users_common_settings.common_settings["enable_sites_preview"])
