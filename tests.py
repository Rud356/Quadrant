import requests

s = requests.session()
s2 = requests.session()
link = "http://localhost:5000"
headers = {
    "api_version": "1.0.0",
}

def authorize_user(login, pwd, sess):
    auth = {
        "login": login,
        "password": pwd
    }
    r = sess.post(link+"/api/users/login", json=auth, headers=headers)
    print(r.status_code)
    return r.json()

def send_friend_request(sess):
    r = sess.post(link+"/api/users/my/friends/5ebd4f331d4cd5908f3d192d", headers=headers, cookies=dict(sess.cookies))
    print(r.text)


def accept(sess):
    r = sess.post(link+"/api/users/my/pendings/5ec33eb5cd27ba0fef4d1854?=1", headers=headers, cookies=dict(sess.cookies))
    return r
user = authorize_user("hello_world1234", "hello_world123456", s)
user_2 = authorize_user("hello_bbbbbbbbb12", "World_bbbbbbbbb12", s2)
print(s2.get(link+"/api/users/my/pendings", headers=headers, cookies=dict(s2.cookies)).text)
# print(accept(s2).text)
# send_friend_request(s)

