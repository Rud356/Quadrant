import unittest
from typing import List, NamedTuple
from uuid import UUID

from Quadrant.models import users_package
from Quadrant.models.db_init import Session
from Quadrant.models.users_package import UsersRelationType, UsersRelations
from tests.datasets import async_drop_db, async_init_db, create_user
from tests.utils import clean_tests_folders, make_async_call


class UserData(NamedTuple):
    name: str
    login: str
    password: str

# TODO: fix freezes on finishing tests


class TestUsersFunctionality(unittest.TestCase):
    @classmethod
    @make_async_call
    async def setUpClass(cls) -> None:
        cls.session = Session()
        await async_init_db()

    async def create_users(self, *users_data: UserData) -> List[users_package.User]:
        users = []
        for user_data in users_data:

            user_auth = await create_user(
                user_data.name, user_data.login, user_data.password, self.session
            )
            users.append(user_auth.user)

        return users

    @make_async_call
    async def test_new_users_dont_have_relations(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Rud again", login="Hey, lookin good", password="idk if its a valid but check later"),
            UserData(name="Rud tests stuff", login="Just an example", password="i Suppose Talking here is ok")
        )
        relations_status = await UsersRelations.get_any_relationships_status(
            user_1.id, user_2.id, session=self.session
        )
        self.assertEqual(relations_status, UsersRelationType.none)

    @make_async_call
    async def test_users_dont_have_relations_with_not_existing_user(self):
        user_1, *_ = await self.create_users(
            UserData(name="Rud again", login="Trying this", password="Magic happening"),
        )
        relations_status = await UsersRelations.get_any_relationships_status(
            user_1.id, UUID('683a2e17-934a-42e0-852d-e642ddcf2863'), session=self.session
        )
        self.assertEqual(relations_status, UsersRelationType.none)

    @make_async_call
    async def test_sending_friend_request_to_himself(self):
        user_1, *_ = await self.create_users(
            UserData(name="Rud plays around again", login="stuff is hard too", password="but work pls"),
        )
        with self.assertRaises(ValueError):
            await UsersRelations.send_friend_request(user_1, user_1, session=self.session)

    @make_async_call
    async def test_sending_and_getting_friend_request(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Rud again here", login="really hope it works", password="i guess it's fine"),
            UserData(name="Rud talking", login="Just an example again", password="no password checks")
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.friend_request_sender)
        self.assertEqual(user_2_relation, UsersRelationType.friend_request_receiver)

    @make_async_call
    async def test_accepting_friend_request(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Rud doing tests 2", login="bombs, ropes?", password="we got em"),
            UserData(name="Rud: insanity", login="frozen but its google", password="translate")
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        await UsersRelations.respond_on_friend_request(user_1, user_2, accept_request=True, session=self.session)
        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.friends)
        self.assertEqual(user_2_relation, UsersRelationType.friends)

    @make_async_call
    async def test_rejecting_friend_request(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Bad apple", login="but something", password="is a database"),
            UserData(name="Wassup gamers", login="break it down", password="fireworks are all around")
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        await UsersRelations.respond_on_friend_request(user_1, user_2, accept_request=False, session=self.session)
        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.none)
        self.assertEqual(user_2_relation, UsersRelationType.none)

    @make_async_call
    async def test_sending_friend_request_twice(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Here we go", login="we gotta go", password="deeper"),
            UserData(name="Tick-tack", login="your time is running", password="out of universe")
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)

        with self.assertRaises(UsersRelations.exc.RelationshipsException):
            await UsersRelations.send_friend_request(user_1, user_2, session=self.session)

    @make_async_call
    async def test_sending_friend_request_to_someone_who_sent_it(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Its fun to do", login="there's no meaning", password="idk why i write this here"),
            UserData(name="Tick-tack boom", login="gotta go", password="out of bounds")
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)

        with self.assertRaises(UsersRelations.exc.RelationshipsException):
            await UsersRelations.send_friend_request(user_2, user_1, session=self.session)

    @make_async_call
    async def test_cancelling_friend_request_twice(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Dante", login="do you have some demons?", password="pizza"),
            UserData(name="Sand which", login="i ran out of creativity", password="too hard already")
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        await UsersRelations.cancel_friend_request(user_1, user_2, session=self.session)

        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.none)
        self.assertEqual(user_2_relation, UsersRelationType.none)

    @make_async_call
    async def test_cancelling_not_existing_request(self):
        user_1, *_ = await self.create_users(
            UserData(name="Rud plays around", login="stuff is hard", password="but working"),
        )
        with self.assertRaises(UsersRelations.exc.RelationshipsException):
            await UsersRelations.cancel_friend_request(user_1, user_1, session=self.session)

    @make_async_call
    async def test_removing_friend(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Rud doing tests 3", login="too lazy to make jokes", password="i'm tried"),
            UserData(name="Send help", login="There's a lot of code", password="at least it looks ok")
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        await UsersRelations.respond_on_friend_request(user_1, user_2, accept_request=True, session=self.session)
        await UsersRelations.remove_user_from_friends(user_1, user_2, session=self.session)

        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.none)
        self.assertEqual(user_2_relation, UsersRelationType.none)

    @make_async_call
    async def test_removing_not_friend(self):
        user_1, *_ = await self.create_users(
            UserData(name="Rud doing tests 4", login="idk wts", password="idk what i am"),
        )
        with self.assertRaises(UsersRelations.exc.RelationshipsException):
            await UsersRelations.remove_user_from_friends(
                user_1, user_1, session=self.session
            )

    @make_async_call
    async def test_blocking_users(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Jane", login="perplexing_dual", password="pre-historic age"),
            UserData(name="Diary", login="bring me back 2007th", password="september burns")
        )
        await UsersRelations.block_user(user_1, user_2, session=self.session)
        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.blocked)
        self.assertEqual(user_2_relation, UsersRelationType.none)

    @make_async_call
    async def test_blocking_already_blocked_users(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Brain", login="just login", password="nothing interesting"),
            UserData(name="HaHaHa", login="why so serious?", password="I think its funny")
        )
        await UsersRelations.block_user(user_2, user_1, session=self.session)
        with self.assertRaises(UsersRelations.exc.AlreadyBlockedException):
            await UsersRelations.block_user(user_2, user_1, session=self.session)

    @make_async_call
    async def test_blocking_blocking_himself(self):
        user_1, *_ = await self.create_users(
            UserData(name="So hard", login="just pls", password="don't break"),
        )
        with self.assertRaises(ValueError):
            await UsersRelations.block_user(user_1, user_1, session=self.session)

    @make_async_call
    async def test_blocking_user_in_relations(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Pack", login="reverse order", password="just come and see"),
            UserData(name="It's hard to come up with", login="creative things", password="in here, yknow?")
        )

        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        await UsersRelations.block_user(user_1, user_2, session=self.session)

        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.blocked)
        self.assertEqual(user_2_relation, UsersRelationType.none)

    @make_async_call
    async def test_blocking_each_other(self):
        user_1, user_2 = await self.create_users(
            UserData(name="Fanny Pack", login="CoD", password="and others"),
            UserData(name="Hope any of those are funny", login="cuz its hard", password="#blabbering")
        )

        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        await UsersRelations.block_user(user_2, user_1, session=self.session)
        await UsersRelations.block_user(user_1, user_2, session=self.session)

        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.blocked)
        self.assertEqual(user_2_relation, UsersRelationType.blocked)

    @make_async_call
    async def test_unblocking_user(self):
        user_1, user_2 = await self.create_users(
            UserData(name="I ran out of fuel", login="I need healing", password="this gonna be meme hell"),
            UserData(name="Why?", login="Cuz", password="i can")
        )
        await UsersRelations.block_user(user_1, user_2, session=self.session)
        user_1_relation = await UsersRelations.get_exact_relationship_status(user_1.id, user_2.id, session=self.session)
        user_2_relation = await UsersRelations.get_exact_relationship_status(user_2.id, user_1.id, session=self.session)

        self.assertEqual(user_1_relation, UsersRelationType.blocked)
        self.assertEqual(user_2_relation, UsersRelationType.none)

    @make_async_call
    async def test_viewing_relations_page(self):
        user_1, user_2 = await self.create_users(
            UserData(
                name="Rud goes rounds and rounds", login="creative things to say ended for now",
                password="i guess it's ok, only guess"
            ),
            UserData(
                name="Rud talking with himself", login="is it even healthy?",
                password="IDK, just i wanna finish stuff"
            )
        )
        await UsersRelations.send_friend_request(user_1, user_2, session=self.session)
        page = await UsersRelations.get_relationships_page(
            user_1, page=0, relationship_type=UsersRelationType.friend_request_sender, session=self.session
        )

        # Gets by first index a first relation record and then first field (status)
        self.assertEqual(page[0][0], UsersRelationType.friend_request_sender)

    @classmethod
    @make_async_call
    async def tearDownClass(cls) -> None:
        clean_tests_folders()
        await cls.session.close()
        await async_drop_db()
