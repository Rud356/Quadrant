from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import BigInteger, Column, Enum, ForeignKey, and_, or_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from Quadrant.models.db_init import Base
from Quadrant.models.users.relations_types import UsersRelationType
from .user import User

USERS_RELATIONS_PER_PAGE = 50


class UsersRelations(Base):
    relation_id = Column(BigInteger, primary_key=True)
    initiator_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    relation_with_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    relation_status = Column(Enum(UsersRelationType), default=UsersRelationType.none, nullable=False)

    @staticmethod
    def any_user_initialized_relationship(user_id: User.id, with_user_id: User.id):
        return or_(
            and_(UsersRelations.initiator_id == user_id, UsersRelations.relation_with_id == with_user_id),
            and_(UsersRelations.initiator_id == with_user_id, UsersRelations.relation_with_id == user_id)
        )

    @staticmethod
    async def get_relationships_status_with(user_id: User.id, with_user_id: User.id, *, session) -> UsersRelationType:
        relation_result = await session.execute(
            select(UsersRelations.relation_status).filter(
                UsersRelations.any_user_initialized_relationship(user_id, with_user_id)
            )
        )
        relation = await relation_result.scalar()

        if relation is None:
            return UsersRelationType.none

        return relation

    @staticmethod
    async def get_exact_relationship_with_user(
        user: User, with_user_id: User.id, *, session: AsyncSession
    ) -> Tuple[UsersRelations, User]:
        relation, relation_with = await (
            await session.execute(
                select(UsersRelations, User).filter(
                    UsersRelations.any_user_initialized_relationship(user.id, with_user_id)
                ).join(User, User.id == with_user_id)
            )
        ).one()

        return relation, relation_with

    @staticmethod
    async def get_exact_relationship_status(user_id: User.id, with_user_id: User.id, *, session) -> UsersRelationType:
        relation = await (
            await session.execute(
                select(UsersRelations.relation_status).filter(
                    UsersRelations.initiator_id == user_id,
                    UsersRelations.relation_with_id == with_user_id
                )
            )
        ).scalar_one_or_none()

        if relation is None:
            return UsersRelationType.none

        return relation

    @classmethod
    async def get_exact_relationship(
        cls, user_id: User.id, with_user_id: User.id, *, session
    ) -> Optional[UsersRelations]:
        relation = await (
            await session.execute(
                select(cls).filter(
                    UsersRelations.initiator_id == user_id,
                    UsersRelations.relation_with_id == with_user_id
                )
            )
        ).one_or_none()

        return relation

    @staticmethod
    async def get_relationships_page(
        user: User, page: int, relationship_type: UsersRelationType, *, session
    ) -> Tuple[Tuple[UsersRelations, User]]:
        if page < 0:
            raise ValueError("Invalid page")

        results = await (
            await session.execute(
                select(UsersRelations, User).filter(
                    or_(
                        UsersRelations.initiator_id == user.id,
                        UsersRelations.relation_with_id == user.id
                    ),
                    UsersRelations.relation_status.is_(relationship_type)
                ).join(User, User.id != user.id)
                .limit(UsersRelations).offset(USERS_RELATIONS_PER_PAGE * page)
            )
        ).all()

        return tuple(  # noqa: alchemy objects
            ((relation, relation_with) for relation, relation_with in results)
        )

    @staticmethod
    async def add_friend_request(request_from: User, request_to: User, *, session) -> bool:
        relationships_status: UsersRelationType = await UsersRelations.get_relationships_status_with(
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
    async def respond_on_friend_request(from_user: User, to_user_id: User.id, accept_request: bool, *, session) -> bool:
        relationships_status: UsersRelationType = await UsersRelations.get_exact_relationship_status(
            to_user_id, from_user.id, session=session
        )

        if relationships_status == UsersRelationType.friend_request_receiver:
            users_relations_query = UsersRelations.any_user_initialized_relationship(from_user.id, to_user_id)
            if accept_request:
                await session.execute(
                    update(UsersRelations).where(users_relations_query).values(
                        relation_status=relationships_status.friends
                    ).execution_options(synchronize_session="fetch")
                )

            else:
                await session.execute(
                    delete(UsersRelations).where(users_relations_query)
                    .execution_options(synchronize_session="fetch")
                )

            await session.commit()
            return True

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationships to become friends")

    @staticmethod
    async def cancel_friend_request(from_user: User, to_user_id: User.id, *, session) -> bool:
        relationships_status: UsersRelationType = await UsersRelations.get_exact_relationship_status(
            to_user_id, from_user.id, session=session
        )

        if relationships_status == UsersRelationType.friend_request_sender:
            users_relations_query = UsersRelations.any_user_initialized_relationship(to_user_id, from_user)

            await session.execute(
                delete(UsersRelations).where(users_relations_query)
                .execution_options(synchronize_session="fetch")
            )
            await session.commit()
            return True

        else:
            raise UsersRelations.exc.RelationshipsException("Invalid relationships to cancel friend request")

    @staticmethod
    async def block_user(block_by: User, blocking_user: User, *, session) -> UsersRelations:
        # There only max of two relations and we should make sure that we're not unblocking someone unintentionally
        initialized_by_blocker: UsersRelations = await UsersRelations.get_exact_relationship(
            block_by, blocking_user, session=session
        )
        initialized_by_blocking_user: UsersRelations = await UsersRelations.get_exact_relationship(
            blocking_user, block_by, session=session
        )

        if initialized_by_blocker is None:
            initialized_by_blocker = UsersRelations(
                initiator_id=block_by.id,
                relation_with_id=blocking_user.id,
                relation_status=UsersRelationType.blocked
            )
            session.add(initialized_by_blocker)

        elif initialized_by_blocker.relation_status == UsersRelationType.blocked:
            raise ValueError("User is already blocked")

        else:
            initialized_by_blocker.relation_status = UsersRelationType.blocked

        if (
            (initialized_by_blocking_user is not None) and
            (initialized_by_blocking_user.relation_status != UsersRelationType.blocked)
        ):
            session.delete(initialized_by_blocking_user)

        await session.commit()
        return initialized_by_blocker

    @staticmethod
    async def unblock_user(user_unblock_initializer: User, unblocking_user: User, *, session) -> bool:
        relation = await UsersRelations.get_exact_relationship_status(
            user_unblock_initializer, unblocking_user.id, session=session
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
        return True

    class exc:
        class RelationshipsException(Exception):
            pass

        class BlockedRelationshipException(RelationshipsException):
            pass
