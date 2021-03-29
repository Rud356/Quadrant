from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import BigInteger, Column, Enum, ForeignKey, and_, or_

from .db_init import Base
from .relations_types import UsersRelationType
from .user_model import User

USERS_RELATIONS_PER_PAGE = 50


class UsersRelations(Base):
    relation_id = Column(BigInteger, primary_key=True)
    initiator_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    relation_with_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    relation_status = Column(Enum(UsersRelationType), default=UsersRelationType.none, nullable=False)

    @staticmethod
    async def check_relationships_with(user: User, with_user: User.id, *, session) -> UsersRelationType:
        relation = await session.query(UsersRelations.relation_status).filter(
            or_(
                and_(UsersRelations.initiator_id == user.id, UsersRelations.relation_with_id == with_user.id),
                and_(UsersRelations.initiator_id == with_user.id, UsersRelations.relation_with_id == user.id)
            )
        ).scalar()

        if relation is None:
            return UsersRelationType.none

        return relation

    @staticmethod
    async def get_relationship_with_including_user(
        user: User, with_user: User.id, *, session
    ) -> Tuple[UsersRelations, User]:
        relation, relation_with = await session.query(UsersRelations, User).filter(
            or_(
                and_(UsersRelations.initiator_id == user.id, UsersRelations.relation_with_id == with_user.id),
                and_(UsersRelations.initiator_id == with_user.id, UsersRelations.relation_with_id == user.id)
            )
        ).join(User, User.id != user.id).one()

        return relation, relation_with

    @staticmethod
    async def get_exact_relationship_status(user: User, with_user: User.id, *, session) -> UsersRelationType:
        relation = await session.query(UsersRelations.relation_status).filter(
            UsersRelations.initiator_id == user.id,
            UsersRelations.relation_with_id == with_user.id
        ).scalar()

        if relation is None:
            return UsersRelationType.none

        return relation

    @staticmethod
    async def get_relationships_page(
        user: User, page: int, relationship_type: UsersRelationType, *, session
    ) -> Tuple[Tuple[UsersRelations, User]]:
        if page < 0:
            raise ValueError("Invalid page")

        results = await session.query(UsersRelations, User).filter(
            or_(UsersRelations.initiator_id == user.id, UsersRelations.relation_with_id == user.id),
            UsersRelations.relation_status.is_(relationship_type)
        ).join(User, User.id != user.id) \
            .limit(UsersRelations).offset(USERS_RELATIONS_PER_PAGE * page).all()

        return tuple( # noqa: alchemy objects
            ((relation, relation_with) for relation, relation_with in results)
        )

    @staticmethod
    def users_relationship_query(to_user: User, from_user: User, *, session):
        return session.query(UsersRelations).filter(
            or_(
                and_(
                    UsersRelations.initiator_id == to_user.id,
                    UsersRelations.relation_with_id == from_user.id
                ),
                and_(
                    UsersRelations.initiator_id == from_user.id,
                    UsersRelations.relation_with_id == to_user.id
                )
            )
        )

    @staticmethod
    async def add_friend_request(request_from: User, request_to: User, *, session) -> bool:
        relationships_status: UsersRelationType = await UsersRelations.check_relationships_with(
            request_from, request_to.id, session=session
        )

        if relationships_status == UsersRelationType.none:
            friend_request_outgoing = UsersRelations(
                initiator_id=request_from.id, relation_with_id=request_to.id,
                relationships_status=UsersRelationType.friend_request_sender
            )
            friend_request_incoming = UsersRelations(
                initiator_id=request_to.id, relation_with_id=request_from.id,
                relationships_status=UsersRelationType.friend_request_receiver
            )

            session.add_all([friend_request_outgoing, friend_request_incoming])
            await session.commit()

            return True

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationship type")

    @staticmethod
    async def respond_on_friend_request(from_user: User, to_user: User, accept_request: bool, *, session) -> bool:
        relationships_status: UsersRelationType = await UsersRelations.get_exact_relationship_status(
            to_user, from_user.id, session=session
        )

        if relationships_status == UsersRelationType.friend_request_receiver:
            users_relations_query = UsersRelations.users_relationship_query(from_user, to_user, session=session)
            if accept_request:
                users_relations_query.update({'relation_status': relationships_status.friends})
                await session.commit()
                return True

            else:
                users_relations_query.delete()
                await session.commit()
                return True

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationships to become friends")

    @staticmethod
    async def cancel_friend_request(from_user: User, to_user: User, *, session) -> bool:
        relationships_status: UsersRelationType = await UsersRelations.get_exact_relationship_status(
            to_user, from_user.id, session=session
        )

        if relationships_status == UsersRelationType.friend_request_sender:
            UsersRelations.users_relationship_query(to_user, from_user, session=session).delete()
            await session.commit()
            return True

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationships to cancel friend request")

    @staticmethod
    async def block_user(block_by: User, blocking_user: User, *, session) -> UsersRelations:
        # There only max of two relations and we should make sure that we're not unblocking someone unintentionally
        relations: Tuple[UsersRelations] = await UsersRelations.users_relationship_query(
            block_by, blocking_user, session=session
        ).all()
        initialized_by_blocker: Optional[UsersRelations] = None
        initialized_by_blocking_user: Optional[UsersRelations] = None

        for relation in relations:
            if relation.initiator_id == blocking_user.id:
                initialized_by_blocking_user = relation

            if relation.initiator_id == block_by.id:
                initialized_by_blocker = relation

        if initialized_by_blocker.relation_status == UsersRelationType.blocked:
            raise ValueError("User is already blocked")

        if initialized_by_blocker is not None:
            initialized_by_blocker.relation_status = UsersRelationType.blocked

        else:
            initialized_by_blocker = UsersRelations(
                initiator_id=block_by.id,
                relation_with_id=blocking_user.id,
                relation_status=UsersRelationType.blocked
            )
            session.add(initialized_by_blocker)

        if (
            (initialized_by_blocking_user is not None) and
            (initialized_by_blocking_user.relation_status != UsersRelationType.blocked)
        ):
            initialized_by_blocking_user.relation_status.delete()

        await session.commit()
        return initialized_by_blocker

    @staticmethod
    async def unblock_user(user_unblock_initializer: User, unblocking_user: User, *, session) -> bool:
        relation = await UsersRelations.get_exact_relationship_status(
            user_unblock_initializer, unblocking_user.id, session=session
        )

        if relation != UsersRelationType.blocked:
            raise UsersRelations.exc.RelationshipsException("Invalid relation ship to unblock user")

        session.query(UsersRelations).filter(
            UsersRelations.initiator_id == user_unblock_initializer.id,
            UsersRelations.relation_with_id == unblocking_user.id
        ).delete()

        await session.commit()
        return True

    class exc:
        class RelationshipsException(Exception):
            pass

        class BlockedRelationshipException(RelationshipsException):
            pass
