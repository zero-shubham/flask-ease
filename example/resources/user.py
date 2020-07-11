from application import (
    my_api,
    ResponseModel,
    Depends,
    Security,
    oauth2_scheme
)
from schemas.user import (
    UserInResp,
    UserCreation,
    UsersInResp
)
from models.User import (
    User
)
from uuid import UUID, uuid4
from utils.dependencies import (
    get_current_user
)


@my_api.get(
    route="/users",
    response_models=[
        ResponseModel(
            model_schema=UsersInResp,
            status_code=200,
            description="Success"
        )
    ],
    tags=["users"],
    auth_required=True
)
def get_all_users(
    offset: int = 0,
    limit: int = 10,
    user=Depends(get_current_user)
):
    """
    Get user by id.
    """
    users = User.get_all_users(
        offset,
        limit
    )
    count = User.get_all_users_count()
    return UsersInResp(
        users=users,
        total_count=count
    ), 200


@my_api.post(
    route="/users",
    response_models=[
        ResponseModel(
          model_schema=UserInResp,
            status_code=200,
            description="Success"
        )
    ],
    tags=["users"]
)
def create_new_user(
    obj_in: UserCreation
):
    """
    Create new user.
    """
    new_user = User(
        id=uuid4(),
        **obj_in.dict()
    )
    new_user.save_to_db()
    return new_user.json(), 200
