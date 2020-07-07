import asyncio
import unittest
from os import system, mkdir
from random import choices
from string import ascii_letters

import requests

from app_config import tests_config
from setup_tests import drop_db, setup_for_tests

system('cls')

auth_credentials = {
    'login': tests_config['login'],
    'password': tests_config['password']
}
second_auth_credentials = {
    'login': tests_config['second_login'],
    'password': tests_config['second_password']
}

base_url = 'http://127.0.0.1/api'
loop = asyncio.get_event_loop()


def create_authorized_session(auth):
    sess = requests.session()
    r = sess.post(base_url + "/user/login", json=auth)
    return sess, r.json()

# !TEST CAN BE RUNNED ONLY ONCE PER APP START
# TODO: tests will be broken with this update cuz of
# moving setters routes into one and
# making pagination for some routes with big output


class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.sess, self.val = create_authorized_session(
            auth_credentials
        )
        self.sess2, self.val2 = create_authorized_session(
            second_auth_credentials
        )

    @classmethod
    def setUpClass(cls):
        try:
            loop.run_until_complete(setup_for_tests())
        except ValueError:
            pass

    def test_001_about_me(self):
        r = self.sess.get(base_url+"/user/me")
        self.assertEqual(r.status_code, 200)

    def test_002_set_nick(self):
        r = self.sess.post(
            base_url+"/me/nick",
            params={"new_nick": "hello tester"}
        )
        self.assertEqual(r.status_code, 200)

    def test_003_too_long_nick(self):
        r = self.sess.post(base_url+"/me/nick", params={"new_nick": "b"*26})
        self.assertEqual(r.status_code, 400)

    def test_004_too_short_nick(self):
        r = self.sess.post(base_url+"/me/nick", params={"new_nick": ''})
        self.assertEqual(r.status_code, 400)

    def test_005_set_friendcode(self):
        r = self.sess.post(
            base_url+"/me/friend_code",
            params={"code": ''.join(choices(ascii_letters, k=25))}
        )
        self.assertEqual(r.status_code, 200)

    def test_006_set_friendcode_second(self):
        code = ''.join(choices(ascii_letters, k=25))
        r = self.sess2.post(base_url+"/me/friend_code", params={"code": code})
        self.assertEqual(r.status_code, 200)

    def test_007_set_invalid_friendcode(self):
        r = self.sess.post(base_url+"/me/friend_code", params={"code": "b"*51})
        self.assertEqual(r.status_code, 400)

    def test_008_set_text_status(self):
        r = self.sess.post(base_url+"/me/text_status", json={
            "text_status": "hello and welcome to the tests"
        })
        self.assertEqual(r.status_code, 200)

    def test_009_set_invalid_text_status(self):
        r = self.sess.post(base_url+"/me/text_status", json={
            "text_status": "1"*257
        })
        self.assertEqual(r.status_code, 400)

    def test_010_set_empty_text_status(self):
        r = self.sess.post(base_url+"/me/text_status", json={
            "text_status": ""
        })
        self.assertEqual(r.status_code, 200)

    def test_011_frineds(self):
        r = self.sess.get(base_url+"/friends")
        self.assertEqual(r.status_code, 200)

    def test_012_set_status(self):
        r = self.sess.post(base_url+"/me/status/1")
        self.assertEqual(r.status_code, 200)

    def test_013_set_invalid_status(self):
        r = self.sess.post(base_url+"/me/status/10")
        self.assertEqual(r.status_code, 400)

    def test_014_get_user(self):
        r = self.sess.get(
            base_url+f"/user/{self.val2['response']['user']['_id']}"
        )
        self.assertEqual(r.status_code, 200)

    def test_015_get_invalid_user(self):
        r = self.sess.get(base_url+"/user/313342313213")
        self.assertEqual(r.status_code, 400)

    def test_016_get_endpoints(self):
        r = self.sess.get(base_url+"/endpoints")
        self.assertEqual(r.status_code, 200)

    def test_017_create_dm(self):
        with_user = self.val2['response']['user']['_id']
        payload = {
            'with': with_user
        }
        r = self.sess.post(
            base_url+"/endpoints/create_endpoint/dm",
            json=payload
        )
        self.assertEqual(r.status_code, 200)

    def test_018_create_invalid_dm(self):
        with_user = '12w123213232'
        payload = {
            'with': with_user
        }
        r = self.sess.post(
            base_url+"/endpoints/create_endpoint/dm",
            json=payload
        )
        self.assertEqual(r.status_code, 404)

    @unittest.expectedFailure
    def test_019_a_creating_dm_again(self):
        with_user = self.val2['response']['user']['_id']
        payload = {
            'with_user': with_user
        }
        r = self.sess.post(
            base_url+"/endpoints/create_endpoint/dm",
            json=payload
        )
        self.assertEqual(r.status_code, 200)

    def test_020_get_endpoint(self):
        r = self.sess.get(base_url+"/endpoints")
        self.assertEqual(r.status_code, 200)

    def test_021_get_exact_endpoint(self):
        r = self.sess.get(base_url+"/endpoints").json()
        endpoints = r['response']
        r = self.sess.get(base_url+f"/endpoints/{endpoints[0]}")
        self.assertEqual(r.status_code, 200)

    def test_022_post_message(self):
        r = self.sess.get(base_url+"/endpoints").json()
        endpoints = r['response']
        endpoint = endpoints[0]
        msg = {
            "content": "Hello world!",
        }
        r = self.sess.post(
            base_url+f"/endpoints/{endpoint}/messages",
            json=msg
        )
        self.assertEqual(r.status_code, 200)

    def test_023_get_messages(self):
        r = self.sess.get(base_url+"/endpoints").json()
        endpoints = r['response']
        endpoint = endpoints[0]

        r = self.sess.get(base_url+f"/endpoints/{endpoint}/messages")
        self.assertEqual(r.status_code, 200)

    def test_024_send_friend_request(self):
        r = self.sess.post(
            base_url+f"/friends/{self.val2['response']['user']['_id']}"
        )
        self.assertEqual(r.status_code, 200)

    def test_025_get_outgoing_requests(self):
        r = self.sess.get(base_url+"/outgoing_requests")
        self.assertEqual(r.status_code, 200)

    def test_026_get_incoming_requests(self):
        r = self.sess2.get(base_url+"/incoming_requests")
        self.assertEqual(r.status_code, 200)

    def test_027_cancel_outgoing_request(self):
        r = self.sess.get(base_url+"/outgoing_requests").json()
        user_id = self.val2['response']['user']['_id']
        r = self.sess.delete(base_url+f"/outgoing_requests/{user_id}")
        self.assertEqual(r.status_code, 200)

    def test_028_cancel_incoming_request(self):
        self.test_024_send_friend_request()
        r = self.sess2.get(base_url+"/incoming_requests").json()
        friend = r['response']

        r = self.sess2.post(
            base_url+f"/incoming_requests/{friend[0]}",
            params={
                "accept": False
            }
        )
        self.assertEqual(r.status_code, 200)

    def test_029_cancel_incoming_not_requested(self):
        user_id = self.val2['response']['user']['_id']
        r = self.sess2.post(
            base_url+f"/incoming_requests/{user_id}",
            params={
                "accept": False
            }
        )
        self.assertEqual(r.status_code, 404)

    def test_030_cancel_invalid_id(self):
        r = self.sess2.post(
            base_url+"/incoming_requests/2332123213", params={
                "accept": False
            }
        )
        self.assertEqual(r.status_code, 400)

    def test_031_send_friendcode_request(self):
        r = self.sess.post(base_url + "/friends/request", params={
            "code": self.val2['response']['user']['code']
        })
        self.assertEqual(r.status_code, 200)

    def test_032_accept_friend_request(self):
        r = self.sess2.get(base_url+"/incoming_requests").json()
        friend = r['response'][0]
        r = self.sess2.post(base_url+f"/incoming_requests/{friend}", params={
            "accept": "True"
        })

        self.assertEqual(r.status_code, 200)

    def test_033_delete_friend(self):
        r = self.sess.get(base_url+"/friends").json()
        friend = r['response'][0]
        r = self.sess.delete(base_url+f"/friends/{friend['_id']}")
        self.assertEqual(r.status_code, 200)

    def test_034_delete_friend_already(self):
        r = self.sess.delete(
            base_url+f"/friends/{self.val2['response']['user']['_id']}"
        )
        self.assertEqual(r.status_code, 400)

    def test_035_delete_friend_invalid_id(self):
        r = self.sess.delete(base_url+"/friends/21873782136")
        self.assertEqual(r.status_code, 404)

    def test_036_blocked_route(self):
        r = self.sess.get(base_url + "/blocked")
        self.assertEqual(r.status_code, 200)

    def test_037_block_friend(self):
        r = self.sess.post(
            base_url+f"/blocked/{self.val2['response']['user']['_id']}"
        )
        self.assertEqual(r.status_code, 200)

    def test_038_blocking_again(self):
        r = self.sess.post(
            base_url+f"/blocked/{self.val2['response']['user']['_id']}"
        )
        self.assertEqual(r.status_code, 204)

    def test_039_user_blocking_ivalid(self):
        r = self.sess.post(base_url+"/blocked/12323144321")
        self.assertEqual(r.status_code, 400)

    def test_040_unblock_user(self):
        r = self.sess.delete(
            base_url+f"/blocked/{self.val2['response']['user']['_id']}"
        )
        self.assertEqual(r.status_code, 200)

    def test_041_unblock_user_again(self):
        r = self.sess.delete(
            base_url+f"/blocked/{self.val2['response']['user']['_id']}"
        )
        self.assertEqual(r.status_code, 204)

    def test_042_unblock_user_invalid(self):
        r = self.sess.delete(base_url+"/blocked/12323144321")
        self.assertEqual(r.status_code, 400)

    def test_043_send_message_with_file(self):
        try:
            mkdir('temp/')
        except FileExistsError:
            ...

        with open('temp/text.txt', 'w') as f:
            f.write("A"*42)

        r = self.sess.get(base_url+"/endpoints").json()
        endpoints = r['response']
        endpoint = endpoints[0]

        with open("temp/text.txt", 'rb') as f:
            send_files = {"file_1": f}
            r = self.sess.post(base_url+"/files/upload", files=send_files)
        r = r.json()
        msg = {
            "content": "Hello world with files!",
            "files": r['response']
        }
        r = self.sess.post(
            base_url+f"/endpoints/{endpoint}/messages",
            json=msg
        )

        self.assertEqual(r.status_code, 200)

    def tearDown(self):
        self.sess.close()
        self.sess2.close()

    @classmethod
    def tearDownClass(cls):
        loop.run_until_complete(drop_db())


if __name__ == "__main__":
    unittest.defaultTestLoader.sortTestMethodsUsing = None
    unittest.main()
