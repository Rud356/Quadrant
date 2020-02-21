import peewee

from models.conf import db_engine
from models.friends import FriendList

class UserModel(peewee.Model):
    id: int = peewee.BigAutoField()
    name: str = peewee.CharField(50)
    bot: bool = peewee.BooleanField(default=False)

    _token: str = peewee.TextField(unique=True)
    _login: str = peewee.TextField(unique=True)
    _password: str = peewee.TextField()

    @staticmethod
    def get_by_id(id: int):
        try:
            user = UserModel.get(UserModel.id == id)
            return user
        except peewee.DoesNotExist:
            raise UserModel.custom_exc.NotExistingUser("No user with such id")

    @staticmethod
    def auth_token(token: str):
        user = UserModel.get(UserModel._token == token)
        if user is None:
            raise UserModel.custom_exc.NotExistingUser("No user with this token")
        return user

    @staticmethod
    def auth_login(login: str, password: str):
        user = UserModel.get(
            UserModel._login == login
            and
            UserModel._password == password
        )
        if user is None:
            raise UserModel.custom_exc.NotExistingUser("No user with this token")
        return user

    @staticmethod
    def add_friend(added_friend: int, added_by: int):
        return FriendList.add_friend(
            added_friend,
            added_by
        )

    @staticmethod
    def get_all_friends(user_id: int):
        return FriendList.get_all_friends(user_id)

    class custom_exc:
        class NotExistingUser(Exception): pass

    class Meta:
        database = db_engine