import json
import asyncio
import unittest

import aiohttp
import websockets
import fastjsonschema

from test._test_utils import create_user, rand_string, drop_db
from app import load_config

config = load_config()


class TestRelationRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loop = asyncio.get_event_loop()

        login, password = loop.run_until_complete(create_user())
        second_login, second_password = loop.run_until_complete(create_user())

        cls.first_session = loop.run_until_complete(cls.authorize(
            login, password, loop
        ))

        cls.second_session = loop.run_until_complete(cls.authorize(
            second_login, second_password, loop
        ))

        cls.first_friend_code = cls.set_friend_code(
            cls.first_session, loop, "http://localhost:{}/api".format(
                config.getint("App", "port")
            )
        )
        for cookie in cls.first_session.cookie_jar:
            if cookie.key == 'token':
                cls.token_1 = cookie.value

        for cookie in cls.second_session.cookie_jar:
            if cookie.key == 'token':
                cls.token_2 = cookie.value

        cls.second_friend_code = cls.set_friend_code(
            cls.second_session, loop, "http://localhost:{}/api".format(
                config.getint("App", "port")
            )
        )

        cls.loop = loop
        cls.base_url = "http://localhost:{}/api".format(
            config.getint("App", "port")
        )
        cls.base_ws = "ws://localhost:{}/api".format(
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

    @staticmethod
    def set_friend_code(session, loop, base):
        update_payload = {
            "friend_code": rand_string(25)
        }

        async def request():
            r = await session.post(
                base + "/me/update",
                json=update_payload
            )

            return r

        loop.run_until_complete(request())
        return update_payload['friend_code']

    def test_send_friend_code_request_and_cancel_by_acceptor(self):
        async def request():
            async with websockets.connect(self.base_ws + "/ws") as ws:
                await ws.send(
                    json.dumps({
                        "token": self.token_1
                    })
                )

                r = await self.second_session.post(
                    self.base_url + "/friends/request", params={
                        "code": self.first_friend_code
                    }
                )

                ws_r = await ws.recv()
                ws_r = await ws.recv()
                ws_r = json.loads(ws_r)

                fastjsonschema.validate(
                    {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "type": {"type": "integer"}
                        }
                    }, ws_r
                )

                self.assertEqual(r.status, 200)

                r = await self.first_session.get(
                    self.base_url + "/friends/incoming_requests"
                )
                r = await r.json()

                user_id = list(r.keys())[0]

                r = await self.first_session.delete(
                    self.base_url + f"/friends/incoming_requests/{user_id}"
                )

                self.assertEqual(r.status, 200)

                ws_r = await ws.recv()
                ws_r = await ws.recv()
                ws_r = json.loads(ws_r)

                fastjsonschema.validate(
                    {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "type": {"type": "integer"}
                        }
                    }, ws_r
                )

        self.loop.run_until_complete(request())

    def test_send_friend_code_request_and_cancel_by_initiator(self):
        async def request():
            async with websockets.connect(self.base_ws + "/ws", close_timeout=2000) as ws:
                await ws.send(
                    json.dumps({
                        "token": self.token_1
                    })
                )

                r = await self.second_session.post(
                    self.base_url + "/friends/request", params={
                        "code": self.first_friend_code
                    }
                )

                ws_r = await ws.recv()
                ws_r = await ws.recv()
                ws_r = json.loads(ws_r)

                fastjsonschema.validate(
                    {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "type": {"type": "integer"}
                        }
                    }, ws_r
                )

                self.assertEqual(r.status, 200)

                r = await self.second_session.get(
                    self.base_url + "/friends/outgoing_requests"
                )
                r = await r.json()

                user_id = list(r.keys())[0]

                r = await self.second_session.delete(
                    self.base_url + f"/friends/outgoing_requests/{user_id}"
                )

                self.assertEqual(r.status, 200)

                ws_r = await ws.recv()
                ws_r = await ws.recv()
                ws_r = json.loads(ws_r)

                fastjsonschema.validate(
                    {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "type": {"type": "integer"}
                        }
                    }, ws_r
                )

        self.loop.run_until_complete(request())

    def test_send_friend_code_request_accept_and_remove_friend(self):
        async def request():
            async with websockets.connect(self.base_ws + "/ws") as ws:
                await ws.send(
                    json.dumps({
                        "token": self.token_1
                    })
                )

                r = await self.second_session.post(
                    self.base_url + "/friends/request", params={
                        "code": self.first_friend_code
                    }
                )

                ws_r = await ws.recv()
                ws_r = await ws.recv()
                ws_r = json.loads(ws_r)

                fastjsonschema.validate(
                    {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "type": {"type": "integer"}
                        }
                    }, ws_r
                )

                self.assertEqual(r.status, 200)

                r = await self.first_session.get(
                    self.base_url + "/friends/incoming_requests"
                )
                r = await r.json()

                user_id = list(r.keys())[0]

                r = await self.first_session.post(
                    self.base_url + f"/friends/incoming_requests/{user_id}",
                    params={"accept": "True"}
                )

                self.assertEqual(r.status, 200)

                ws_r = await ws.recv()
                ws_r = await ws.recv()
                ws_r = json.loads(ws_r)

                fastjsonschema.validate(
                    {
                        "type": "object",
                        "properties": {
                            "_id": {"type": "string"},
                            "type": {"type": "integer"}
                        }
                    }, ws_r
                )

        self.loop.run_until_complete(request())

    @classmethod
    def tearDownClass(cls):
        async def close_session(session):
            await session.close()

        cls.loop.run_until_complete(close_session(cls.first_session))
        cls.loop.run_until_complete(close_session(cls.second_session))
        cls.loop.run_until_complete(drop_db())
