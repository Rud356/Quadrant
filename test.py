import requests
import unittest

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

    def tearDown(self):
        self.sess.close()
        self.sess2.close()

if __name__ == "__main__":
    unittest.main()