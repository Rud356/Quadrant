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


user = authorize_user("hello_world1234", "hello_world123456", s)
user_2 = authorize_user("hello_bbbbbbbbb12", "World_bbbbbbbbb12", s2)
# send_friend_request(s)