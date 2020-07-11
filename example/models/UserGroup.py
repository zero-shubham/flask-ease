from db import db
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy import (
    String,
    ForeignKey,
    select,
    func
)
from uuid import UUID as UID

_user_group_table_name = "user_groups"


class UserGroup(db.Model):
    __tablename__ = _user_group_table_name
    id = db.Column(UUID, primary_key=True)
    group = db.Column(String, unique=True)

    def __init__(self, id: UID, group: str):
        self.id = str(id)
        self.group = group

    def json(self):
        return {
            "id": self.id,
            "group": self.group
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_group(cls, group):
        return cls.query.filter_by(group=group).first()

    @classmethod
    def get_all_user_groups(
        cls,
        offset: int = 0,
        limit: int = 10
    ):
        user_groups = cls.query.offset(0).limit(limit).all()
        user_groups = [user_group.json() for user_group in user_groups]
        return user_groups

    @classmethod
    def get_all_user_groups_count(cls):
        return db.session.query(cls).count()
