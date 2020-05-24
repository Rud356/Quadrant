import requests
import unittest
from os import system
from config import tests_config

system('cls')

auth_credentials = {
    'login':tests_config['login'],
    'password':tests_config['password']
}
second_auth_credentials = {
    'login':tests_config['second_login'],
    'password':tests_config['second_password']
}

base_url = 'http://localhost/api'

def create_authorized_session(auth):
    sess = requests.session()
    r = sess.post(base_url + "/user/login", json=auth)
    print("Authorized:", r.status_code)
    return sess


class TestUserRoutes(unittest.TestCase):
    def setUp(self):
        self.sess = create_authorized_session(auth_credentials)
        self.sess2 = create_authorized_session(second_auth_credentials)

    def test_about_me(self):
        r = self.sess.get("/user/me")
        self.assertEqual(r.status_code, 200)

    def test_set_nick(self):
        r = self.sess.post("/user/me/nick", params={"new_nick": "hello tester"})
        self.assertEqual(r.status_code, 200)

    def test_too_long_nick(self):
        r = self.sess.post("/user/me/nick", params={"new_nick": "b"*26})
        self.assertEqual(r.status_code, 400)

    def test_too_short_nick(self):
        r = self.sess.post("/user/me/nick", params={"new_nick": ''})
        self.assertEqual(r.status_code, 400)

    def test_set_friendcode(self):
        r = self.sess.post("/user/me/friend_code", params={"code": "hello world"})
        self.assertEqual(r.status_code, 200)

    def test_set_invalid_friendcode(self):
        r = self.sess.post("/user/me/friend_code", params={"code": "b"*51})
        self.assertEqual(r.status_code, 400)

    def test_set_text_status(self):
        r = self.sess.post("/user/me/text_status", json={
            "text_status": "hello and welcome to the tests"
        })
        self.assertEqual(r.status_code, 200)

    def test_set_invalid_text_status(self):
        r = self.sess.post("/user/me/text_status", json={
            "text_status": "1"*256
        })
        self.assertEqual(r.status_code, 400)

    def test_set_empty_text_status(self):
        r = self.sess.post("/user/me/text_status", json={
            "text_status": ""
        })
        self.assertEqual(r.status_code, 200)