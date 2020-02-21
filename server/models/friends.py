import peewee
from models.conf import db_engine
from models.user import UserModel

class FriendList(peewee.Model):
    friends_of_user = peewee.ForeignKeyField(
        UserModel, backref='+'
    )
    users_friends = peewee.ForeignKeyField(
        UserModel, backref='friends'
    )

    @staticmethod
    def get_all_friends(user_id):
        try:
            return FriendList.get(
                FriendList.users_friends,
                FriendList.friends_of_user == user_id
            )
        except peewee.DoesNotExist:
            return []

    @staticmethod
    def add_friend(added_friend: int, added_by: int):
        try:
            added_by: UserModel = UserModel.get_by_id(added_by)
            added_friend: UserModel = UserModel.get_by_id(added_friend)
            if not added_by.bot and not added_friend.bot:
                FriendList.create(
                    friend_of_user=added_by.id,
                    users_friend=added_friend.id
                )

                FriendList.create(
                    friend_of_user=added_friend.id,
                    users_friend=added_by.id
                )
            else:
                return False
        except UserModel.custom_exc.NotExistingUser:
            return False

    @staticmethod
    def delete_friend(deleting_by: int, deleted: int):
        try:
            deleted: UserModel = UserModel.get_by_id(deleted)
            deleting_by: UserModel = UserModel.get_by_id(deleting_by)
            if not deleting_by.bot and deleted.bot:
                try:
                    deleted.friends.get(
                        FriendList.friends_of_user == deleted.id,
                        FriendList.users_friend == deleting_by.id
                    ).delete_instance()

                    deleting_by.friends.get(
                        FriendList.friends_of_user == deleting_by.id,
                        FriendList.users_friend == deleted.id
                    ).delete_instance()
                except peewee.DoesNotExist:
                    return False
                return True
        except UserModel.custom_exc.NotExistingUser:
            return False

    class Meta:
        database = db_engine