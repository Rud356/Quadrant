import requests
import unittest
from os import system
from tests import schemas
from config import tests_config

system('cls')
base_url = 'http://localhost/api/%s'


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


# TODO: somehow add cleanup of db
class UserRoutesTest(unittest.TestCase):
    def registrate(self):
        self.session = create_session()
        self.session2 = create_session()
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
        self.session.post(base_url % '/users/registrate', json=reg_first)
        self.session2.post(base_url % '/users/registrate', json=reg_first)

    def authorize(self):
        r = self.session.post(base_url % '/login', json=auth_credentials)
        if r.status_code == 401:
            self.fail(
                "You must register user manually before "
                "testing and put his credentials int config.cfg"
            )
            return

        self.assertEqual(r.status_code, 200)

    def about_me(self):
        user = self.session.get(base_url % '/users/me').json()
        schemas.user_self(user)

    def set_nick(self):
        new_nick = 'tester123'
        nick = self.session.post(base_url % f'/me/nick?new_nick={new_nick}').json()

        self.assertEqual(nick['responce'], new_nick)

    @unittest.expectedFailure
    def set_null_nick(self):
        r = self.session.post(base_url % '/me/nick?new_nick=')
        assert r.status_code == 400

    @unittest.expectedFailure
    def set_too_long_nick(self):
        r = self.session.post(base_url % '/me/nick?new_nick=111111111111111111111111111111111111111111111111111')
        assert r.status_code == 400

    def set_friend_code(self):
        code = 'tester123'
        r = self.session.post(base_url % f'/me/friendcode?code={code}').json()

        self.assertEqual(r['responce'], code)

    @unittest.expectedFailure
    def set_none_friend_code(self):
        r = self.session.post(base_url % f'/me/friendcode?code=')
        assert r.status_code == 400

    @unittest.expectedFailure
    def set_too_long_friend_code(self):
        r = self.session.post(base_url % f'/me/friendcode?code=111111111111111111111111111111111111111111111111111')
        assert r.status_code == 400

    def set_status(self):
        new_status = 2
        r = self.session.post(base_url % f'/me/status/{new_status}')
        self.assertEqual(r.status_code, 200)

    @unittest.expectedFailure
    def set_invalid_status(self):
        new_status = 15
        r = self.session.post(base_url % f'/me/status/{new_status}')
        self.assertEqual(r.status_code, 200)

    # put your another user id
    def get_user_from_id(self):
        id = "5ebd4f331d4cd5908f3d192d"
        r = self.session.get(base_url % f'/users/{id}').json()
        schemas.user_from_id(r)

    @unittest.expectedFailure
    def get_invalid_user(self):
        r = self.session.get(base_url % '/users/123nope').json()
        schemas.user_from_id(r)

    def get_friends(self):
        r = self.session.get(base_url % '/friends')
        self.assertEqual(r.status_code, 200)

    def get_blocked(self):
        r = self.session.get(base_url % '/blocked')
        self.assertEqual(r.status_code, 200)

    #TODO: add test for getting some exact user