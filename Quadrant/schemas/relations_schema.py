from typing import List
from uuid import UUID

from Quadrant.models.users_package.relations_types import UsersRelationType
from pydantic import BaseModel, Field


class RelationWithUser(BaseModel):
    with_user_id: UUID = Field(description="User, with whom you've checked relations")
    status: UsersRelationType = Field(description="represents which relations you have with this user")


class RelationsPage(BaseModel):
    relation_type: UsersRelationType
    relations_with_users_ids: List[UUID]


class RelationsPagesCount(BaseModel):
    relation_type: UsersRelationType
    pages: int = Field("Shows how many pages of relation of this exact type can be fetched")


class UnfriendedUserNotification(BaseModel):
    unfriended_user_id: UUID = Field(description="User id who's not your friend anymore")


class BlockedNotification(BaseModel):
    blocked_user_id: UUID = Field(description="User id who was blocked")


class RemovedFromBlockNotification(BaseModel):
    unblocked_user_id: UUID = Field(description="User id who was unblocked")


class ResponseOnIncomingFriendRequest(BaseModel):
    response_to: UUID = Field(description="User if of someone to whom we responded")
    accepted_request: UUID = Field(description="Shows if user accepted request of whom we responding to")


class FriendRequestSent(BaseModel):
    friend_request_receiver_id: UUID = Field(description="User id who received friend request")


class CancelledFriendRequest(BaseModel):
    friend_request_receiver_id: UUID = Field(description="User id who received friend request")
    friend_request_sender_id: UUID = Field(description="User id who cancelled friend request")
