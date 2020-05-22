import asyncio
import requests
import unittest
import websockets
from os import system
from tests import schemas
from config import tests_config

system('cls')
base_url = 'http://localhost/api'


def create_session():
    headers = {
        "api_version": "1.0.0"
    }
    sess = requests.session()
    sess.headers = headers

    return sess


auth_credentials = {
    'login':tests_config['login'],
    'password':tests_config['password']
}
second_auth_credentials = {
    'login':tests_config['second_login'],
    'password':tests_config['second_password']
}
session = create_session()
session2 = create_session()

# TODO: somehow add cleanup of db
class TestUserRoutes(unittest.TestCase):
    def test_registrate(self):
        reg_first = {
            "nick": "Tester1",
            "bot": False,
            **auth_credentials,
        }
        reg_second = {
            "nick": "Tester2",
            "bot": False,
            **second_auth_credentials,
        }
        session.post(base_url + '/users/registrate', json=reg_first)
        session2.post(base_url + '/users/registrate', json=reg_second)
        print('reg', 1)

    def test_authorize(self):
        r = session.post(base_url + '/users/login', json=auth_credentials)
        if r.status_code == 401:
            self.fail(
                "You must register user manually before "
                "testing and put his credentials int config.cfg"
            )
            return
        print(r.text)
        print(session.cookies)
        print('auth', 2)
        self.assertEqual(r.status_code, 200)

    def test_auth_second(self):
        r = session.post(base_url + '/users/login', json=second_auth_credentials)
        print('sec auth', 3)

    def test_about_me(self):
        user = session.get(base_url + '/users/me').json()
        schemas.user_self(user)
        print('me info', 4)

    def test_set_nick(self):
        new_nick = 'tester123'
        nick = session.post(base_url + f'/me/nick?new_nick={new_nick}').json()
        print('set nick', 5)
        self.assertEqual(nick['response'], new_nick)

    @unittest.expectedFailure
    def test_set_null_nick(self):
        r = session.post(base_url + '/me/nick?new_nick=')
        print('null nick', 6)
        assert r.status_code == 400

    @unittest.expectedFailure
    def test_set_too_long_nick(self):
        r = session.post(base_url + '/me/nick?new_nick=111111111111111111111111111111111111111111111111111')
        print('too long nick', 7)
        assert r.status_code == 400

    def test_set_friend_code(self):
        code = 'tester123'
        r = session.post(base_url + f'/me/friendcode?code={code}').json()
        print('friend code set', 8)

        self.assertEqual(r['response'], code)

    @unittest.expectedFailure
    def test_set_none_friend_code(self):
        r = session.post(base_url + f'me/friendcode?code=')
        print('friend code set none', 8)
        assert r.status_code == 400

    @unittest.expectedFailure
    def test_set_too_long_friend_code(self):
        r = session.post(base_url + f'/me/friendcode?code=111111111111111111111111111111111111111111111111111')
        print('too long friend code', 9)
        assert r.status_code == 400

    def set_status(self):
        new_status = 2
        r = session.post(base_url + f'/me/status/{new_status}')
        print('set status', 9)
        self.assertEqual(r.status_code, 200)

    @unittest.expectedFailure
    def test_set_invalid_status(self):
        new_status = 15
        r = session.post(base_url + f'/me/status/{new_status}')
        print('set invalid status', 10)
        self.assertEqual(r.status_code, 200)

    # put your another user id
    def test_get_user_from_id(self):
        id = "5ebd4f331d4cd5908f3d192d"
        r = session.get(base_url + f'/users/{id}').json()
        print('get another user', 11)
        schemas.user_from_id(r)

    @unittest.expectedFailure
    def test_get_invalid_user(self):
        r = session.get(base_url + '/users/123nope').json()
        print('get invalid user', 12)
        schemas.user_from_id(r)

    def test_get_friends(self):
        r = session.get(base_url + '/friends')
        print('test get friends', 13)
        self.assertEqual(r.status_code, 200)

    def test_get_blocked(self):
        r = session.get(base_url + '/blocked')
        print('test get blocked', 14)
        self.assertEqual(r.status_code, 200)

    #TODO: add test for getting some exact user

if __name__ == "__main__":
    unittest.main()
