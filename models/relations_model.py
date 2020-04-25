import random
from enum import Enum
from datetime import datetime

from app import db, session
from sqlalchemy import (
    Column,
    BigInteger, Enum, ForeignKey,
    and_, or_
)


class Relation(Enum):
    pending = 0
    friends = 1
    blocked = 2


class RelationsModel(db.Model):
    users_relations = Column(ForeignKey('users.id'))
    user_related = Column(ForeignKey('users.id'))
    relation = Column(Enum(Relation))
    __tablename__ = 'relations'


    @staticmethod
    def _get_related_like(user_id, relationship):
        query = session.query(RelationsModel).select()\
            .filter(
                RelationsModel.user_related == user_id,
                RelationsModel.relation == relationship
            )

        return query

    @staticmethod
    def _get_users_relationships(user_id, relationship):
        query = session.query(RelationsModel).select()\
            .filter(
                RelationsModel.users_relations == user_id,
                RelationsModel.relation == relationship
            )

        return query

    @staticmethod
    def _relationship_exists(users_relations, user_related, relation):
        relationship_count = RelationsModel._get_exact_relationship(
            users_relations, user_related, relation
        ).count()

        return bool(relationship_count)

    @staticmethod
    def _has_relationships(user_1, user_2):
        relationship_count = RelationsModel._get_any_relationships(
            user_1, user_2
        ).count()

        return bool(relationship_count)

    @staticmethod
    def _get_any_relationships(user_1, user_2):
        query = session.query(RelationsModel).select()\
            .filter(
                or_(
                    and_(
                        RelationsModel.users_relations == user_2,
                        RelationsModel.user_related == user_1
                    ),
                    and_(
                        RelationsModel.users_relations == user_1,
                        RelationsModel.user_related == user_2
                    )
                )
            )
        return query

    @staticmethod
    def _get_exact_relationship(users_relations, user_related, relation):
        relationship = session.query(RelationsModel).select()\
            .filter(
                and_(
                    RelationsModel.users_relations == users_relations,
                    RelationsModel.user_related == user_related,
                    RelationsModel.relation == relation
                )
            )
        return relationship

    @classmethod
    def send_pending(cls, user_init: int, user_accept: int):
        if cls._has_relationships(user_init, user_accept):
            #? shouldn't have any
            #? they may be already friends
            #? or some of them may have blocked another
            #? or already pending one to another
            raise ValueError('Relationships already exists')

        else:
            new_pending = cls(
                users_relations=user_init,
                user_related=user_accept
            )
            session.add(new_pending)
            session.commit()

    @staticmethod
    def respond_pending(
        user_accept: int, user_init: int,
        accept=True, instant_commit=True
        ):
        relation = RelationsModel._get_exact_relationship(
            user_init, user_accept, Relation.pending
        )
        if not relation.count():
            raise ValueError('No such pending relation')

        session.delete(relation)

        if accept:
            init_friendship = RelationsModel(
                users_relations=user_init,
                user_accept=user_accept,
                relation=Relation.pending
            )
            session.add(init_friendship)

        if instant_commit:
            session.commit()

    @staticmethod
    def delete_friend(
        user_deleter: int, user_with: int,
        instant_commit=True
        ):
        friendship_relation = session.query(RelationsModel)\
            .select().filter(
                or_(
                    and_(
                        RelationsModel.users_relations == user_deleter,
                        RelationsModel.user_related == user_with,
                        RelationsModel.relation == Relation.friends
                    ),
                    and_(
                        RelationsModel.users_relations == user_with,
                        RelationsModel.user_related == user_deleter,
                        RelationsModel.relation == Relation.friends
                    )
                )
            )

        if friendship_relation.count():
            session.delete(friendship_relation)

            if instant_commit:
                session.commit()
                return True
        else:
            return False

    @staticmethod
    def block_user(user_ask: int, user_to_block: int):
        other_relations = RelationsModel.select()\
            .filter(
                or_(
                    and_(
                        RelationsModel.users_relations == user_ask,
                        RelationsModel.user_related == user_to_block,
                        RelationsModel.relation != Relation.blocked
                    ),
                    and_(
                        RelationsModel.users_relations == user_ask,
                        RelationsModel.user_related == user_to_block,
                        RelationsModel.relation != Relation.blocked
                    )
                )
            )


        is_blocked = RelationsModel._get_exact_relationship(
            user_ask, user_to_block, Relation.blocked
        ).count()

        if is_blocked:
            raise ValueError('User already blocked this user')

        new_block = RelationsModel(
            RelationsModel.users_relations == user_ask,
            RelationsModel.user_related == user_to_block,
            RelationsModel.relation == Relation.blocked
        )

        session.delete(other_relations)
        session.add(new_block)
        session.commit()

    @staticmethod
    def unblock_user(user_ask: int, user_unblocking: int):
        relation = RelationsModel._get_exact_relationship(
            user_ask, user_unblocking, Relation.blocked
        )
        session.delete(relation)
        session.commit()
