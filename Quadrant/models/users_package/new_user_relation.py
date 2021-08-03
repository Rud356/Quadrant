from __future__ import annotations

from math import ceil
from typing import List, Union
from uuid import UUID

from sqlalchemy import (
    Column, Enum, ForeignKey,
    PrimaryKeyConstraint, and_, func,
    select, delete
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, relationship

from Quadrant.models.db_init import AsyncSession, Base
from Quadrant.models.users_package.relations_types import UsersRelationType
from Quadrant.quadrant_logging import gen_log
from Quadrant.schemas.relations_schema import RelationsPage
from .user import User, UsersStatus

USERS_RELATIONS_PER_PAGE = 100


class UserRelation(Base):
    initiator_user_id: Mapped[UUID] = Column(ForeignKey('users.id'), nullable=False, index=True)
    with_user_id: Mapped[UUID] = Column(ForeignKey('users.id'), nullable=False, index=True)
    status: Mapped[UsersRelationType] = Column(
        Enum(UsersRelationType),
        default=UsersRelationType.none,
        nullable=False
    )

    opposite_relation: UserRelation = relationship(
        "UserRelation", foreign_keys=[initiator_user_id, with_user_id], lazy="joined",

    )
    __tablename__ = "users_relations"
    __table_args__ = (
        PrimaryKeyConstraint("initiator_user_id", "with_user_id", name="pk_relations_of_users"),
    )

    async def accept_friend_request(self, *, session: AsyncSession) -> None:
        """
        Accepts friend request from other user.

        :param session: sqlalchemy session.
        :return: nothing.
        """
        if self.status != UsersRelationType.friend_request_receiver:
            text = (
                f"{self.initiator_user_id} isn't in relation "
                f"{UsersRelationType.friend_request_receiver.name}"
                f"(actual relationship is {self.status.name}) with {self.with_user_id}"
            )
            gen_log.debug(text)
            raise self.exc.InvalidRelationshipStatus(text)

        self.status = UsersRelationType.friends
        self.opposite_relation.status = UsersRelationType.friends
        await session.commit()

    async def deny_friend_request(self, *, session: AsyncSession) -> None:
        """
        Denies friend request from other user.

        :param session: sqlalchemy session.
        :return: nothing.
        """
        if self.status != UsersRelationType.friend_request_receiver:
            text = (
                f"{self.initiator_user_id} isn't in relation "
                f"{UsersRelationType.friend_request_receiver.name}"
                f"(actual relationship is {self.status.name}) with {self.with_user_id}"
            )
            gen_log.debug(text)
            raise self.exc.InvalidRelationshipStatus(text)

        query = self._delete_relationship_if_not_blocked(self.initiator_user_id, self.with_user_id)
        await session.execute(query)
        await session.commit()

    async def cancel_friend_request(self, *, session: AsyncSession) -> None:
        """
        Cancels sent friend request.

        :param session: sqlalchemy session.
        :return: nothing.
        """
        if self.status != UsersRelationType.friend_request_sender:
            text = (
                f"{self.initiator_user_id} isn't in relation "
                f"{UsersRelationType.friend_request_sender.name}"
                f"(actual relationship is {self.status.name}) with {self.with_user_id}"
            )
            gen_log.debug(text)
            raise self.exc.InvalidRelationshipStatus(text)

        query = self._delete_relationship_if_not_blocked(self.initiator_user_id, self.with_user_id)
        await session.execute(query)
        await session.commit()

    async def remove_friend(self, *, session: AsyncSession) -> None:
        """
        Removes friend from friend list.

        :param session: sqlalchemy session.
        :return: nothing.
        """
        if self.status != UsersRelationType.friends:
            text = (
                f"{self.initiator_user_id} isn't in relation "
                f"{UsersRelationType.friends.name}"
                f"(actual relationship is {self.status.name}) with {self.with_user_id}"
            )
            gen_log.debug(text)
            raise self.exc.InvalidRelationshipStatus(text)

        query = delete(UserRelation).where(
            and_(
                and_(
                    UserRelation.initiator_user_id.in_([self.with_user_id, self.initiator_user_id]),
                    UserRelation.with_user_id.in_([self.with_user_id, self.initiator_user_id])
                ),
                UserRelation.status == UsersRelationType.friends
            )
        )
        await session.execute(query)
        await session.commit()

    async def unblock_user(self, *, session: AsyncSession) -> None:
        """
        Unblocks user by deleting users relation to other user.

        :param session: sqlalchemy session.
        :return: nothing.
        """
        await session.delete(self)
        await session.commit()

    @classmethod
    async def get_relationship(
        cls, initiator: User, with_user_id: UUID, *, session: AsyncSession
    ) -> UserRelation:
        """
        Gives exact relationship depending on requester id but without instance of User with whom we have it.
        In case found nothing - returns None.

        :param initiator: User instance of someone who is asking for relationship.
        :param with_user_id: user id of someone with whom we look for relation.
        :param session: sqlalchemy session.
        :return: returns exact relationship instance.
        """
        query = select(cls).filter(
            UserRelation.initiator_user_id == initiator.id,
            UserRelation.relation_with_id == with_user_id
        )
        result = await session.execute(query)
        relation = result.scalar_one()

        return relation

    @staticmethod
    async def get_relationship_status(
        initiator_id: UUID, with_user_id: UUID, *, session: AsyncSession
    ) -> UsersRelationType:
        """
        Tells which relation status user has with other user (initiated by requester).

        :param initiator_id: user who asks for relationship.
        :param with_user_id: user with whom initiator has relation.
        :param session: sqlalchemy session.
        :return: one of UsersRelationType.
        """
        query = select(UserRelation.status).filter(
            UserRelation.initiator_user_id == initiator_id,
            UserRelation.relation_with_id == with_user_id
        )
        result = await session.execute(query)
        relation = result.scalar()

        if relation is None:
            return UsersRelationType.none

        return relation

    @staticmethod
    async def is_in_blocked_relations(
        user_id: UUID, other_user_id: UUID, *, session: AsyncSession
    ) -> bool:
        """
        Tells if at least one of users blocked other one.

        :param user_id: first user id.
        :param other_user_id: second user id.
        :param session: sqlalchemy session.
        :return: boolean representing if users are blocked.
        """
        query = select(UserRelation.status == UsersRelationType.blocked).filter(
            and_(
                UserRelation.initiator_user_id.in_([user_id, other_user_id]),
                UserRelation.with_user_id.in_([user_id, other_user_id])
            ),
            UserRelation.status == UsersRelationType.blocked
        )
        result = await session.execute(query)
        relation = result.scalars().all()
        return any(relation)

    @classmethod
    async def send_friend_request(
        cls, initiator: User, to_user: User,
        *, session: AsyncSession
    ) -> UserRelation:
        """
        Sends friend request to other user.
        :param initiator: user who sends friend request.
        :param to_user: user who will receive friend request.
        :param session: sqlalchemy session.
        :return: outgoing friend request relation.
        """

        # TODO: check if other user has any settings that preventing receiving from friend requests
        try:
            friend_request_outgoing = UserRelation(
                initiator_user_id=initiator.id,
                with_user_id=to_user.id,
                status=UsersRelationType.friend_request_sender
            )
            friend_request_incoming = UserRelation(
                initiator_user_id=initiator.id,
                with_user_id=to_user.id,
                status=UsersRelationType.friend_request_receiver
            )

            session.add_all([friend_request_outgoing, friend_request_incoming])
            await session.commit()

            return friend_request_outgoing

        except IntegrityError:
            text = (
                f"{to_user.id} and {initiator.id} have relationships "
                "and so they can not send a friend request to each other"
            )
            gen_log.debug(text)
            raise cls.exc.AlreadyHasRelationship(text)

    @staticmethod
    async def get_relations_page(
        initiator: User, relation_type: UsersRelationType, page: int, *, session: AsyncSession
    ) -> RelationsPage:
        if page < 0:
            raise ValueError("Invalid page")

        query = select(UserRelation.relation_with_id).join(
            (User.username, User.status), User.id == UserRelation.relation_with_id
        )
        query = query.filter(
            and_(
                UserRelation.initiator_user_id == initiator.id,
                UserRelation.status == relation_type
            )
        )
        query = query.limit(USERS_RELATIONS_PER_PAGE).offset(
            USERS_RELATIONS_PER_PAGE * page
        ).order_by(
            User.username,
            User.status.is_(UsersStatus.online)
        )

        result = await session.execute(query)
        relations_with_users_ids: List[UUID] = result.scalars().all()

        packed_relations = RelationsPage.construct(
            relation_type=relation_type,
            relations_with_users_ids=relations_with_users_ids
        )
        return packed_relations

    @staticmethod
    async def get_relations_pages_count(
        initiator: User, relation_type: UsersRelationType, *, session: AsyncSession
    ) -> int:
        query = select(UserRelation.relation_with_id).filter(
            and_(
                UserRelation.initiator_user_id == initiator.id,
                UserRelation.status == relation_type
            )
        ).with_only_columns([func.count()])
        result = await session.execute(query)
        total_relations_records: int = result.scalar()

        return ceil(total_relations_records / USERS_RELATIONS_PER_PAGE)

    @classmethod
    async def block_user(
        cls, initiator: User, blocking_user: User, *, session: AsyncSession
    ) -> UserRelation:
        query = cls._delete_relationship_if_not_blocked(initiator.id, blocking_user.id)
        await session.execute(query)
        new_relation = cls(
            initiator_user_id=initiator.id,
            with_user_id=blocking_user.id,
            status=UsersRelationType.blocked
        )
        session.add(new_relation)
        await session.commit()

        return new_relation

    @staticmethod
    def _delete_relationship_if_not_blocked(
        initiator_user_id: Union[UUID, Mapped[UUID]],
        with_user_id: Union[UUID, Mapped[UUID]]
    ):
        return delete(UserRelation).where(
            and_(
                and_(
                    UserRelation.initiator_user_id.in_([with_user_id, initiator_user_id]),
                    UserRelation.with_user_id.in_([with_user_id, initiator_user_id])
                ),
                UserRelation.status != UsersRelationType.blocked
            )
        )

    class exc:
        class RelationshipsException(Exception):
            """
            Base exception for relationships class.
            """
            pass

        class InvalidRelationshipStatus(RelationshipsException, ValueError):
            """
            Raised when user is in incorrect relationship with other user to perform action.
            """
            pass

        class AlreadyHasRelationship(RelationshipsException):
            """
            Thrown when this relationship type requires
            user to not have any previous relations to other user.
            """

        class AlreadyBlockedException(AlreadyHasRelationship):
            """
            Special exception that represents that user is already blocked.
            """
            pass
