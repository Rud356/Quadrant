from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import (
    BigInteger, Column, Enum, ForeignKey,
    and_, delete, or_, select, update
)
from sqlalchemy.orm import Mapped

from Quadrant.models.db_init import AsyncSession, Base
from Quadrant.models.users_package.relations_types import UsersRelationType
from .user import User

USERS_RELATIONS_PER_PAGE = 50


class UsersRelations(Base):
    relation_id: Mapped[int] = Column(BigInteger, primary_key=True)
    initiator_id: Mapped[UUID] = Column(ForeignKey('users.id'), nullable=False, index=True)
    relation_with_id: Mapped[UUID] = Column(ForeignKey('users.id'), nullable=False, index=True)
    relation_status: Mapped[UsersRelationType] = Column(
        Enum(UsersRelationType), default=UsersRelationType.none, nullable=False
    )

    __tablename__ = "users_relations"

    @staticmethod
    def any_user_initialized_relationship(user_id: User.id, with_user_id: User.id):
        """
        Query part that will give True when any of users pair had initialized relation with other user.

        :param user_id: user id of someone who asks for this.
        :param with_user_id: user id of someone with whom we look for any relations.
        :return: sqlalchemy query.
        """
        return or_(
            and_(UsersRelations.initiator_id == user_id, UsersRelations.relation_with_id == with_user_id),
            and_(UsersRelations.initiator_id == with_user_id, UsersRelations.relation_with_id == user_id)
        )

    @staticmethod
    async def get_any_relationships_status(
        user_id: User.id, with_user_id: User.id, *, session: AsyncSession
    ) -> UsersRelationType:
        """
        Gives relationship status between any of two users.

        :param user_id: user id of someone who asks for this.
        :param with_user_id: user id of someone with whom we look for any relations.
        :param session: sqlalchemy session.
        :return: one of UsersRelationType.
        """
        relation_result = await session.execute(
            select(UsersRelations.relation_status).filter(
                UsersRelations.any_user_initialized_relationship(user_id, with_user_id)
            )
        )
        relation = relation_result.scalar()

        if relation is None:
            return UsersRelationType.none

        return relation

    @staticmethod
    async def get_exact_relationship_with_user(
        user: User, with_user_id: User.id, *, session: AsyncSession
    ) -> Tuple[UsersRelations, User]:
        """
        Gives exact relationship depending of who is requester. Needed for cases when we want unblock other user
        or send him an friend request.

        :param user: user instance of someone who asks for this.
        :param with_user_id: user id of someone with whom we look for relation.
        :param session: sqlalchemy session.
        :return: UsersRelations instance and instance of User with whom requester have some relationship.
        """
        query = select(UsersRelations, User).filter(
            UsersRelations.initiator_id == user.id,
            UsersRelations.relation_with_id == with_user_id
        ).join(User, User.id == with_user_id)
        result = await session.execute(query)
        relation, relation_with = result.scalar_one()

        return relation, relation_with

    @classmethod
    async def get_exact_relationship(
        cls, user_id: User.id, with_user_id: User.id, *, session: AsyncSession
    ) -> Optional[UsersRelations]:
        """
        Gives exact relationship depending on requester id but without instance of User with whom we have it.
        In case found nothing - returns None.

        :param user_id: requester id.
        :param with_user_id: user id of someone with whom we look for relation.
        :param session: sqlalchemy session.
        :return: returns exact relationship instance of
        """
        query = select(cls).filter(
            UsersRelations.initiator_id == user_id,
            UsersRelations.relation_with_id == with_user_id
        )
        result = await session.execute(query)
        relation = result.scalar_one_or_none()

        return relation

    @staticmethod
    async def get_exact_relationship_status(
        user_id: User.id, with_user_id: User.id, *, session: AsyncSession
    ) -> UsersRelationType:
        """
        Gives exact relation status with user depending on requester id.

        :param user_id: requester id.
        :param with_user_id: user id of someone with whom we look for relation.
        :param session: sqlalchemy session.
        :return: one of UsersRelationType.
        """
        query = select(UsersRelations.relation_status).filter(
            UsersRelations.initiator_id == user_id,
            UsersRelations.relation_with_id == with_user_id
        )
        query_result = await session.execute(query)
        relation = query_result.scalar()

        if relation is None:
            return UsersRelationType.none

        return relation

    @staticmethod
    async def get_relationships_page(
        user: User, page: int, relationship_type: UsersRelationType,
        *, session: AsyncSession
    ) -> List[Dict[UsersRelations.relation_status, User.id]]:
        """
        Gives page of relationships ordered by username and users with who Users instances with whom has relations.

        :param user: user instance of someone who asks for this.
        :param page: page number.
        :param relationship_type: filter by type of requester to other user relation.
        :param session: sqlalchemy session.
        :return: relationship status and User instance with whom we have it.
        """
        if page < 0:
            raise ValueError("Invalid page")

        query = select(UsersRelations.relation_status, User.id).join(User, User.id != user.id)
        # Since we have relations records created for both users - we can easily just look only for initiator id
        query = query.filter(
            UsersRelations.initiator_id == user.id,
            UsersRelations.relation_status == relationship_type
        )
        query = query.limit(USERS_RELATIONS_PER_PAGE).offset(USERS_RELATIONS_PER_PAGE * page) \
            .order_by(User.username)

        result = await session.execute(query)
        relations = result.all()

        packed_relations = []
        for relation, user_id in relations:
            packed_relations.append({"status": relation, "with_user_id": user_id})

        return relations

    @staticmethod
    async def send_friend_request(
        request_sender: User, request_receiver: User, *, session: AsyncSession
    ) -> None:
        """
        Sending friend request to someone.

        :param request_sender: who authored request.
        :param request_receiver: who will receive it.
        :param session: sqlalchemy session.
        :return: nothing (raises exception if something's wrong).
        """
        relationships_status: UsersRelationType = await UsersRelations.get_any_relationships_status(
            request_sender.id, request_receiver.id, session=session
        )

        # TODO: check if receiver user allowed to send friend requests
        if request_receiver.is_bot:
            raise request_receiver.exc.UserIsBot("Bot users can not receive friend requests")

        if request_receiver.id == request_sender.id:
            raise ValueError("User can not become friend with himself")

        if relationships_status == UsersRelationType.none:
            friend_request_outgoing = UsersRelations(
                initiator_id=request_sender.id, relation_with_id=request_receiver.id,
                relation_status=UsersRelationType.friend_request_sender
            )
            friend_request_incoming = UsersRelations(
                initiator_id=request_receiver.id, relation_with_id=request_sender.id,
                relation_status=UsersRelationType.friend_request_receiver
            )

            session.add_all([friend_request_outgoing, friend_request_incoming])
            await session.commit()

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationship type")

    @staticmethod
    async def cancel_friend_request(
        canceller: User, friend_request_to: User, *, session: AsyncSession
    ) -> None:
        """
        Cancels sent friend request.

        :param canceller: user that sent friend request.
        :param friend_request_to: user who received request.
        :param session: sqlalchemy session.
        :return: nothing (raises exception if something's wrong).
        """
        relationships_status: UsersRelationType = await UsersRelations.get_exact_relationship_status(
            canceller.id, friend_request_to.id, session=session
        )

        if relationships_status != UsersRelationType.friend_request_sender:
            raise UsersRelations.exc.RelationshipsException("You can not cancel not existing friend request")

        users_relations_query = UsersRelations.any_user_initialized_relationship(canceller.id, friend_request_to.id)
        query = delete(UsersRelations).where(
            and_(
                users_relations_query,
                UsersRelations.relation_status.in_(
                    [UsersRelationType.friend_request_receiver, UsersRelationType.friend_request_sender]
                )
            )
        ).execution_options(synchronize_session="fetch")

        await session.execute(query)
        await session.commit()

    @staticmethod
    async def respond_on_friend_request(
        request_receiver: User, request_sender: User, accept_request: bool,
        *, session: AsyncSession
    ) -> None:
        """
        Responds on friend request by adding a new friend or rejecting request.

        :param request_receiver: user that received friend request.
        :param request_sender: user who authored request.
        :param accept_request: bool flag that shows that request was accepted or not.
        :param session: sqlalchemy session.
        :return: nothing (raises exception if something's wrong).
        """
        relationships_status: UsersRelationType = await UsersRelations.get_exact_relationship_status(
            request_sender.id, request_receiver.id, session=session
        )

        if relationships_status == UsersRelationType.friend_request_receiver:
            users_relations_query = UsersRelations.any_user_initialized_relationship(
                request_receiver.id, request_sender.id
            )

            if accept_request:
                query = update(UsersRelations).where(users_relations_query).values(
                    relation_status=relationships_status.friends
                ).execution_options(synchronize_session="fetch")
                await session.execute(query)

            else:
                query = delete(UsersRelations).where(
                    and_(
                        users_relations_query,
                        UsersRelations.relation_status.in_(
                            [UsersRelationType.friend_request_receiver, UsersRelationType.friend_request_sender]
                        )
                    )
                ).execution_options(synchronize_session="fetch")
                await session.execute(query)

            await session.commit()

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationships to become friends")

    @staticmethod
    async def remove_user_from_friends(
        removed_by: User, friend: User, *, session: AsyncSession
    ) -> None:
        """
        Removes friend from friend list if he's in or if user isn't in - raises error.

        :param removed_by: user that wants to remove someone from friends.
        :param friend: user that will be removed from friends.
        :param session: sqlalchemy session.
        :return: nothing (raises exception if something's wrong).
        """
        relationships_status: UsersRelationType = await UsersRelations.get_any_relationships_status(
            friend.id, removed_by.id, session=session
        )

        if relationships_status == UsersRelationType.friends:
            users_relations_query = UsersRelations.any_user_initialized_relationship(removed_by.id, friend.id)
            query = delete(UsersRelations).where(
                and_(
                    users_relations_query,
                    UsersRelations.relation_status == UsersRelationType.friends
                )
            ).execution_options(synchronize_session="fetch")

            await session.execute(query)
            await session.commit()

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationships to become friends")

    @staticmethod
    async def block_user(
        blocking_by: User, blocking_user: User, *, session: AsyncSession
    ) -> UsersRelations:
        """
        Destroys friends relationship, requester or receiver of friend request and sets relationship status, that
        initiated by blocking_by user, to UsersRelationType.blocked.
        Must not remove all relationships to be able keep other's user
        possible block relationship still existing.

        :param blocking_by: user who blocks other user.
        :param blocking_user: user who blocking_by wants to block.
        :param session: sqlalchemy session.
        :return: updated or relationship, initialized by blocking_by.
        """
        # There only max of two relations and we should make sure that we're not unblocking someone unintentionally
        if blocking_user.id == blocking_by.id:
            raise ValueError("Can not block yourself")

        initialized_by_blocker: UsersRelations = await UsersRelations.get_exact_relationship(
            blocking_by.id, blocking_user.id, session=session
        )
        initialized_by_blocking_user: UsersRelations = await UsersRelations.get_exact_relationship(
            blocking_user.id, blocking_by.id, session=session
        )

        if initialized_by_blocker is None:
            initialized_by_blocker = UsersRelations(
                initiator_id=blocking_by.id,
                relation_with_id=blocking_user.id,
                relation_status=UsersRelationType.blocked
            )
            session.add(initialized_by_blocker)

        elif initialized_by_blocker.relation_status == UsersRelationType.blocked:
            raise UsersRelations.exc.AlreadyBlockedException("User is already blocked")

        else:
            initialized_by_blocker.relation_status = UsersRelationType.blocked

        if (
            (initialized_by_blocking_user is not None) and
            (initialized_by_blocking_user.relation_status != UsersRelationType.blocked)
        ):
            await session.delete(initialized_by_blocking_user)

        await session.commit()
        return initialized_by_blocker

    @staticmethod
    async def unblock_user(
        user_unblock_initializer: User, unblocking_user: User, *, session: AsyncSession
    ) -> None:
        """
        Unblocks user.

        :param user_unblock_initializer: user who wants to unblock someone.
        :param unblocking_user: user whom he wants to unblock.
        :param session: sqlalchemy session.
        :return: nothing (may raise exceptions).
        """
        relation = await UsersRelations.get_exact_relationship_status(
            user_unblock_initializer.id, unblocking_user.id, session=session
        )

        if relation != UsersRelationType.blocked:
            raise UsersRelations.exc.RelationshipsException("Invalid relation ship to unblock user")

        await session.execute(
            delete(UsersRelations).where(
                UsersRelations.initiator_id == user_unblock_initializer.id,
                UsersRelations.relation_with_id == unblocking_user.id,
                UsersRelations.relation_status.is_(UsersRelationType.blocked)
            )
        )
        await session.commit()

    class exc:
        class RelationshipsException(Exception):
            """
            Base exception for relationships class.
            """
            pass

        class BlockedRelationshipException(RelationshipsException):
            """
            One user blocked another and so anything beside blocking each other can not be performed.
            """
            pass

        class AlreadyBlockedException(BlockedRelationshipException):
            """
            Special exception that represents that user is already blocked
            """
            pass
