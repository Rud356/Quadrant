import unittest
from uuid import UUID

from sqlalchemy import exc

from Quadrant.models.db_init import Session
from Quadrant.models.utils.common_settings_validators import DEFAULT_COMMON_SETTINGS_DICT
from .datasets import create_user, async_init_db, async_drop_db
from .utils import clean_tests_folders, make_async_call


class TestUsersFunctionality(unittest.TestCase):
    @classmethod
    @make_async_call
    async def setUpClass(cls) -> None:
        cls.session = Session()
        await async_drop_db()
        await async_init_db()
        cls.test_user_auth = await create_user("Rud_func", "Rud_functions_tester", "H0w_h4rd_lma0", session=cls.session)
        cls.test_user = cls.test_user_auth.user

    @make_async_call
    async def test_getting_user(self):
        got_user = await self.test_user.get_user(self.test_user.id, session=self.session)
        self.assertEqual(got_user.id, self.test_user.id, f"Somehow user with id {self.test_user.id} didn't got himself")

    @make_async_call
    async def test_getting_not_existing_user(self):
        not_existing_user_id = UUID('683a2e17-934a-42e0-852d-e642ddcf2863')

        with self.assertRaises(exc.NoResultFound):
            await self.test_user.get_user(not_existing_user_id, session=self.session)

    @make_async_call
    async def test_setting_text_status(self):
        new_text_status = "Hello world"
        await self.test_user.set_text_status(new_text_status, session=self.session)
        got_user = await self.test_user.get_user(self.test_user.id, session=self.session)

        self.assertEqual(got_user.text_status, self.test_user.text_status)

    @make_async_call
    async def test_setting_null_text_status(self):
        new_text_status = None

        with self.assertRaises(exc.IntegrityError):
            await self.test_user.set_text_status(
                new_text_status, session=self.session  # noqa: testing that it doesn't works
            )
        await self.session.rollback()

    @make_async_call
    async def test_setting_status(self):
        await self.test_user.set_status("offline", session=self.session)
        got_user = await self.test_user.get_user(self.test_user.id, session=self.session)

        self.assertEqual(got_user.status, self.test_user.status)

    @make_async_call
    async def test_setting_invalid_status(self):
        with self.assertRaises(KeyError):
            await self.test_user.set_status("IDK what i am", session=self.session)

    @make_async_call
    async def test_setting_username(self):
        await self.test_user.set_username("Hello there", session=self.session)
        got_user = await self.test_user.get_user(self.test_user.id, session=self.session)

        self.assertEqual(got_user.username, self.test_user.username)

    @make_async_call
    async def test_users_default_settings_matching_defaults(self):
        test_user_auth = await create_user("Rud_defaults_test", "Rud_default", "SomepwdHere", session=self.session)
        self.assertDictEqual(
            test_user_auth.user.users_common_settings.common_settings,
            DEFAULT_COMMON_SETTINGS_DICT
        )

    @make_async_call
    async def test_updating_settings(self):

        fields_was_updated = await self.test_user.users_common_settings.update_settings(
            settings={"enable_sites_preview": True}, session=self.session
        )
        self.assertEqual(
            tuple(fields_was_updated['updated_settings'].keys()),
            ("enable_sites_preview",)
        )
        self.assertTrue(self.test_user.users_common_settings.common_settings["enable_sites_preview"])

    @classmethod
    @make_async_call
    async def tearDownClass(cls) -> None:
        clean_tests_folders()
        await async_drop_db()
        await cls.session.close()  # noqa: setted in setUpClass
