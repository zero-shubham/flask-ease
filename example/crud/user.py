from application import db
from models.User import User
from core.security import get_password_hash


def get_all_users_in_db(
    offset: int = 0,
    limit: int = 10
):
    query = User.select().offset(offset).limit(limit)
    users = db.engine.execute(query).fetchall()
    return users


def get_all_users_count_in_db():
    query = User.count()
    count = db.session.execute(query).scalar()
    return count


def find_user_by_id(_id):
    query = User.select().where(
        User.columns.id == _id
    )
    user = db.engine.execute(query).fetchone()
    if user:
        return dict(user)


def find_user_by_user_name(user_name):
    query = User.select().where(
        User.columns.email == user_name
    )
    user = db.engine.execute(query).fetchone()
    return dict(user)


def add_new_user_to_db(values: dict):
    values["id"] = str(values["id"])
    values["password"] = get_password_hash(values["password"])
    query = User.insert()
    db.session.execute(query, values)
    db.session.commit()
    new_user = find_user_by_id(values["id"])
    return new_user
