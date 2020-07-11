from db import db
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy import (
    String,
    ForeignKey,
    select,
    func
)
from models.UserGroup import (
    _user_group_table_name
)
from uuid import UUID as UID
from core.security import (
    get_password_hash
)


_user_table_name = "users"


class User(db.Model):
    __tablename__ = _user_table_name

    id = db.Column(UUID, primary_key=True)
    user_name = db.Column(String(length=250), unique=True)
    password = db.Column(String(length=1000))
    group = db.Column("group", ForeignKey(
        f"{_user_group_table_name}.group",
        ondelete="CASCADE"
    ))

    def __init__(self, id: UID, user_name: str, password: str, group: str):
        self.id = str(id)
        self.user_name = user_name
        self.password = get_password_hash(password)
        self.group = group

    def json(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "group": self.group
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, update_list, data):
        for upd in update_list:
            if upd == "user_name":
                self.name = data["user_name"]
            elif upd == "password":
                self.password = generate_password_hash(
                    data["password"]
                )
        self.save_to_db()
        return True

    @classmethod
    def find_by_user_name(cls, user_name):
        return cls.query.filter_by(user_name=user_name).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all_users(
        cls,
        offset: int = 0,
        limit: int = 10
    ):
        users = cls.query.offset(0).limit(limit).all()
        users = [user.json() for user in users]
        return users

    @classmethod
    def get_all_users_count(cls):
        return db.session.query(cls).count()
