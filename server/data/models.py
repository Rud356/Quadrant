play_login = ("hello", "rud")
play_pwd = ("123", "dont fcking use those")
token = "123456"
def authorize_user(login, password):
    return token if password in play_pwd and login in play_login else None