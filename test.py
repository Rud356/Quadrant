import requests
import unittest

from setup_tests import loop, setup_for_tests, drop_db
from os import system
from random import choices
from config import tests_config
from string import ascii_letters

system('cls')

auth_credentials = {
    'login':tests_config['login'],
    'password':tests_config['password']
}
second_auth_credentials = {
    'login':tests_config['second_login'],
    'password':tests_config['second_password']
}

base_url = 'http://127.0.0.1/api'

def create_authorized_session(auth):
    sess = requests.session()
    r = sess.post(base_url + "/user/login", json=auth)
    return sess, r.json()


class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.sess, self.val = create_authorized_session(auth_credentials)
        self.sess2, self.val2 = create_authorized_session(second_auth_credentials)

    @classmethod
    def setUpClass(cls):
        try:
            loop.run_until_complete(setup_for_tests())
        except ValueError:
            pass

    def test_about_me(self):
        r = self.sess.get(base_url+"/user/me")
        self.assertEqual(r.status_code, 200)

    def test_set_nick(self):
        r = self.sess.post(base_url+"/me/nick", params={"new_nick": "hello tester"})
        self.assertEqual(r.status_code, 200)

    def test_too_long_nick(self):
        r = self.sess.post(base_url+"/me/nick", params={"new_nick": "b"*26})
        self.assertEqual(r.status_code, 400)

    def test_too_short_nick(self):
        r = self.sess.post(base_url+"/me/nick", params={"new_nick": ''})
        self.assertEqual(r.status_code, 400)

    def test_set_friendcode(self):
        r = self.sess.post(base_url+"/me/friend_code", params={"code": ''.join(choices(ascii_letters, k=25))})
        self.assertEqual(r.status_code, 200)

    def test_set_invalid_friendcode(self):
        r = self.sess.post(base_url+"/me/friend_code", params={"code": "b"*51})
        self.assertEqual(r.status_code, 400)

    def test_set_text_status(self):
        r = self.sess.post(base_url+"/me/text_status", json={
            "text_status": "hello and welcome to the tests"
        })
        self.assertEqual(r.status_code, 200)

    def test_set_invalid_text_status(self):
        r = self.sess.post(base_url+"/me/text_status", json={
            "text_status": "1"*257
        })
        self.assertEqual(r.status_code, 400)

    def test_set_empty_text_status(self):
        r = self.sess.post(base_url+"/me/text_status", json={
            "text_status": ""
        })
        self.assertEqual(r.status_code, 200)

    def test_frineds(self):
        r = self.sess.get(base_url+"/friends")
        self.assertEqual(r.status_code, 200)

    def test_set_status(self):
        r = self.sess.post(base_url+"/me/status/1")
        self.assertEqual(r.status_code, 200)

    def test_set_invalid_status(self):
        r = self.sess.post(base_url+"/me/status/10")
        self.assertEqual(r.status_code, 400)

    def test_get_user(self):
        r = self.sess.get(base_url+f"/user/{self.val2['response']['user']['_id']}")
        self.assertEqual(r.status_code, 200)

    def test_get_invalid_user(self):
        r = self.sess.get(base_url+f"/user/313342313213")
        self.assertEqual(r.status_code, 400)

    def test_get_endpoints(self):
        r = self.sess.get(base_url+f"/endpoints")
        self.assertEqual(r.status_code, 200)

    def create_dm(self):
        with_user = self.val2['response']['user']['_id']
        payload = {
            'with_user': with_user
        }
        r = self.sess.post(base_url+"/api/endpoint/create_endpoint/dm", json=payload)
        self.assertEqual(r.status_code, 200)

    def create_invalid_dm(self):
        with_user = '12w123213232'
        payload = {
            'with_user': with_user
        }
        r = self.sess.post(base_url+"/api/endpoints/create_endpoint/dm", json=payload)
        self.assertEqual(r.status_code, 404)

    @unittest.expectedFailure
    def test_create_dm_again(self):
        with_user = self.val2['response']['user']['_id']
        payload = {
            'with_user': with_user
        }
        r = self.sess.post(base_url+"/api/endpoints/create_endpoint/dm", json=payload)
        self.assertEqual(r.status_code, 200)

    def test_get_endpoint(self):
        r = self.sess.post(base_url+"/api/endpoints")
        self.assertEqual(r.status_code, 200)

    def test_get_exact_endpoint(self):
        r = self.sess.post(base_url+"/api/endpoints").json()
        endpoints = r['response']
        r = self.sess.post(base_url+f"/api/endpoints/{endpoints[0]}")
        self.assertEqual(r.status_code, 200)

    def test_post_message(self):
        r = self.sess.post(base_url+"/api/endpoints").json()
        endpoints = r['response']
        endpoint = endpoints[0]
        msg = {
            "content": "Hello world!"
        }
        r = self.sess.post(base_url+f"/api/endpoints/{endpoint['_id']}/messages", json=msg)
        self.assertEqual(r.status_code, 200)

    def test_get_messages(self):
        r = self.sess.post(base_url+"/api/endpoints").json()
        endpoints = r['response']
        endpoint = endpoints[0]

        r = self.sess.get(base_url+f"/api/endpoints/{endpoint['_id']}/messages")
        self.assertEqual(r.status_code, 200)

    def test_send_friend_request(self):
        r = self.sess.post(base_url+f"/friends/{self.val2['response']['user']['_id']}")
        self.assertEqual(r.status_code, 200)

    def test_get_outgoing_requests(self):
        r = self.sess.get(base_url+"/outgoing_requests")
        self.assertEqual(r.status_code, 200)

    def test_get_incoming_requests(self):
        r = self.sess2.get(base_url+"/incoming_requests")
        self.assertEqual(r.status_code, 200)

    def test_cancel_outgoing_request(self):
        r = self.sess.get(base_url+"/outgoing_requests").json()
        r = self.sess.delete(base_url+f"/outgoing_requests/{self.val2['response']['user']['id']}")
        self.assertEqual(r.status_code, 200)

    def test_cancel_incoming_request(self):
        r = self.sess2.get(base_url+"/incoming_requests").json()
        friend = r['response'][0]

        r = self.sess2.post(base_url+f"/incoming_requests/{friend}", params={
            "accept": False
        })
        self.assertEqual(r.status_code, 200)

    def test_cancel_not_requested_incoming(self):

        r = self.sess2.post(base_url+f"/incoming_requests/{self.val2['response']['user']['id']}", params={
            "accept": False
        })
        self.assertEqual(r.status_code, 404)

    def test_invalid_id_cancel(self):
        r = self.sess2.post(base_url+f"/incoming_requests/2332123213", params={
            "accept": False
        })
        self.assertEqual(r.status_code, 400)

    def test_send_friendcode_request(self):
        r = self.sess.post(base_url + "/api/friends/request", params={
            "code": self.val2['response']['user']['code']
        })
        self.assertEqual(r.status_code, 200)

    def test_accept_friend_request(self):
        r = self.sess2.get(base_url+"/incoming_requests").json()
        friend = r['response'][0]
        r = self.sess2.post(base_url+f"/incoming_requests/{friend}", params={
            "accept": "True"
        })

        self.assertEqual(r.status_code, 200)

    def test_delete_friend(self):
        r = self.sess.get(base_url+f"/friends").json()
        friend = r['response'][0]
        r = self.sess.delete(base_url+f"/friends/{friend['_id']}")
        self.assertEqual(r.status_code, 200)

    def test_delete_not_friend(self):
        r = self.sess.get(base_url+f"/friends").json()
        friend = r['response'][0]
        r = self.sess.delete(base_url+f"/friends/{friend['_id']}")
        self.assertEqual(r.status_code, 400)

    def test_delete_invalid_id_friend(self):
        r = self.sess.delete(base_url+f"/friends/21873782136")
        self.assertEqual(r.status_code, 404)

    def test_blocked_route(self):
        r = self.sess.get(base_url + "/blocked")
        self.assertEqual(r.status_code, 200)

    def test_block_friend(self):
        r = self.sess.post(base_url+f"/blocked/{self.val2['response']['user']['id']}")
        self.assertEqual(r.status_code, 200)

    def test_again_blocking(self):
        r = self.sess.post(base_url+f"/blocked/{self.val2['response']['user']['id']}")
        self.assertEqual(r.status_code, 204)

    def test_invalid_user_blocking(self):
        r = self.sess.post(base_url+"/blocked/12323144321")
        self.assertEqual(r.status_code, 400)

    def test_unblock_user(self):
        r = self.sess.delete(base_url+f"/blocked/{self.val2['response']['user']['id']}")
        self.assertEqual(r.status_code, 200)

    def test_unblock_again_user(self):
        r = self.sess.delete(base_url+f"/blocked/{self.val2['response']['user']['id']}")
        self.assertEqual(r.status_code, 204)

    def test_unblock_invalid_user(self):
        r = self.sess.delete(base_url+"/blocked/12323144321")
        self.assertEqual(r.status_code, 400)

    def tearDown(self):
        self.sess.close()
        self.sess2.close()

    @classmethod
    def tearDownClass(cls):
        loop.run_until_complete(drop_db())

if __name__ == "__main__":
    unittest.main()