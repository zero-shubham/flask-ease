from application import (
    my_api,
    Depends,
)
from schemas.user import (
    UserInResp,
    UserCreation,
    UsersInResp,
    UserInDB
)
from crud.user import (
    get_all_users_in_db,
    get_all_users_count_in_db,
    add_new_user_to_db
)
from uuid import UUID, uuid4
from utils.dependencies import get_current_user


@my_api.get(
    route="/users",
    response_model=UsersInResp,
    tags=["users"],
    auth_required=True
)
def get_all_users(
    offset: int = 0,
    limit: int = 10,
    current_user=Depends(get_current_user)
):
    """
    Get user by id.
    """
    users = get_all_users_in_db(
        offset,
        limit
    )
    count = get_all_users_count_in_db()
    return UsersInResp(
        users=users,
        total_count=count
    )


@my_api.post(
    route="/users",
    response_model=UserInResp,
    tags=["users"]
)
def create_new_user(
    obj_in: UserCreation
):
    """
    Create new user.
    """
    new_user = add_new_user_to_db(UserInDB(
        id=uuid4(),
        **obj_in.dict()
    ).dict())
    return new_user
