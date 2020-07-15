import asyncio
import unittest

import aiohttp
import fastjsonschema

from test._test_utils import create_user, rand_string
from app import load_config

config = load_config()


class TestUserRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loop = asyncio.get_event_loop()

        cls.login, cls.password = loop.run_until_complete(create_user())
        second_login, second_password = loop.run_until_complete(create_user())
        cls.first_session = loop.run_until_complete(cls.authorize(
            cls.login, cls.password, loop
        ))
        cls.second_session = loop.run_until_complete(cls.authorize(
            second_login, second_password, loop
        ))
        cls.loop = loop
        cls.base_url = "http://localhost:{}/api".format(
            config.getint("App", "port")
        )

    @staticmethod
    async def authorize(login, password, loop):
        session = aiohttp.ClientSession(loop=loop)
        response = await session.post(
            "http://localhost:{}/api/user/login".format(
                config.getint("App", "port")
            ),
            json={
                "login": login,
                "password": password
            }
        )

        if response.status != 200:
            raise ValueError(
                "Cant authorize, invalid response code {}".format(
                    response.status
                )
            )

        return session

    def test_about_me(self):
        async def request():
            r = await self.first_session.get(
                self.base_url + "/user/me"
            )
            return r

        r = self.loop.run_until_complete(request())

        self.assertEqual(r.status, 200)

        user_private_schema = fastjsonschema.compile({
            "type": "object",
            "properties": {
                "_id": {"type": "string"},
                "nick": {"type": "string"},
                "created_at": {"type": "string"},
                "bot": {"type": "boolean"},
                "status": {"type": "integer"},
                "blocked": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "friends": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "pendings_outgoing": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "pendings_incoming": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
            }
        })

        is_valid = user_private_schema(
            self.loop.run_until_complete(r.json())['response']
        )

        self.assertTrue(is_valid)

    def test_update_valid(self):
        update_payload = {
            "nick": rand_string(20),
            "status": 0,
            "text_status": rand_string(15),
            "friend_code": rand_string(25)
        }

        async def request():
            r = await self.first_session.post(
                self.base_url + "/me/update",
                json=update_payload
            )

            return r

        r = self.loop.run_until_complete(request())
        json_response = self.loop.run_until_complete(r.json())['response']
        json_response.pop("_id")
        self.assertEqual(
            json_response,
            update_payload
        )

    @unittest.expectedFailure
    def test_partially_valid_update(self):
        update_payload = {
            "nick": rand_string(55),
            "status": 1,
            "text_status": rand_string(15),
            "friend_code": rand_string(25)
        }

        async def request():
            r = await self.first_session.post(
                self.base_url + "/me/update",
                json=update_payload
            )

            return r

        r = self.loop.run_until_complete(request())
        json_response = self.loop.run_until_complete(r.json())['response']
        json_response.pop("_id")
        self.assertEqual(
            json_response,
            update_payload
        )

    @unittest.expectedFailure
    def test_partially_valid_update_2(self):
        update_payload = {
            "nick": rand_string(20),
            "status": 1,
            "text_status": rand_string(300),
            "friend_code": rand_string(25)
        }

        async def request():
            r = await self.first_session.post(
                self.base_url + "/me/update",
                json=update_payload
            )

            return r

        r = self.loop.run_until_complete(request())
        json_response = self.loop.run_until_complete(r.json())['response']
        json_response.pop("_id")
        self.assertEqual(
            json_response,
            update_payload
        )

    @unittest.expectedFailure
    def test_partially_valid_update_3(self):
        update_payload = {
            "nick": rand_string(20),
            "status": 1,
            "text_status": rand_string(25),
            "friend_code": rand_string(60)
        }

        async def request():
            r = await self.first_session.post(
                self.base_url + "/me/update",
                json=update_payload
            )

            return r

        r = self.loop.run_until_complete(request())
        json_response = self.loop.run_until_complete(r.json())['response']
        json_response.pop("_id")
        self.assertEqual(
            json_response,
            update_payload
        )

    @unittest.expectedFailure
    def test_partially_valid_update_4(self):
        update_payload = {
            "nick": rand_string(20),
            "status": 15,
            "text_status": rand_string(25),
            "friend_code": rand_string(20)
        }

        async def request():
            r = await self.first_session.post(
                self.base_url + "/me/update",
                json=update_payload
            )

            return r

        r = self.loop.run_until_complete(request())
        json_response = self.loop.run_until_complete(r.json())['response']
        json_response.pop("_id")
        self.assertEqual(
            json_response,
            update_payload
        )

    def test_partial_update(self):
        update_payload = {
            "status": 1
        }

        async def request():
            r = await self.first_session.post(
                self.base_url + "/me/update",
                json=update_payload
            )

            return r

        r = self.loop.run_until_complete(request())
        json_response = self.loop.run_until_complete(r.json())['response']
        json_response.pop("_id")
        self.assertEqual(
            json_response,
            update_payload
        )

    def test_keep_alive(self):
        async def request():
            r = await self.first_session.post(
                self.base_url + "/user/keep-alive"
            )

            return r

        r = self.loop.run_until_complete(request())
        self.assertEqual(r.status, 200)

    def test_update_token(self):
        async def request():
            login, password = await create_user()
            new_session = await self.authorize(login, password, self.loop)

            r = await new_session.post(
                self.base_url + "/user/update_token"
            )

            return r

        r = self.loop.run_until_complete(request())
        self.assertEqual(r.status, 200)

    def test_delete_user(self):
        async def request():
            login, password = await create_user()
            new_session = await self.authorize(login, password, self.loop)

            r = await new_session.delete(
                self.base_url + "/user/me"
            )

            return r

        r = self.loop.run_until_complete(request())
        self.assertEqual(r.status, 200)

    @classmethod
    def tearDownClass(cls):
        async def del_users(session):
            await session.delete(
                cls.base_url + "/user/me"
            )
            await session.close()

        cls.loop.run_until_complete(del_users(cls.first_session))
        cls.loop.run_until_complete(del_users(cls.second_session))
        cls.loop.close()
