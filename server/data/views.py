import data.models as models
ids = 0
class User:
    def __init__(self, id, bot, status):
        self.id: int = id
        self.bot: bool = False
        self.status: int = 1

    @classmethod
    def auth(cls, login, pwd):
        ids=1
        token = models.authorize_user(login, pwd)
        print(token)
        if token is not None:
            return token, {token: cls(ids, False, 1)}
        else:
            raise cls.Exceptions.Unauthorized

    class Exceptions:
        class Unauthorized(Exception): pass