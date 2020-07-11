from application import (
    my_api,
    ResponseModel,
    Depends
)
from uuid import UUID, uuid4
from schemas.user_group import (
    UserGroupCreation,
    UserGroupInResp,
    UserGroupsInResp
)
from models.UserGroup import (
    UserGroup
)


@my_api.post(
    route="/user_groups",
    response_models=[
        ResponseModel(
          model_schema=UserGroupInResp,
            status_code=200,
            description="Success"
        )
    ],
    tags=["user_groups"]
)
def create_new_user_group(
    obj_in: UserGroupCreation
):
    """
    Create new user-group.
    """
    new_user_group = UserGroup(
        id=uuid4(),
        **obj_in.dict()
    )
    new_user_group.save_to_db()
    return new_user_group.json(), 200


@my_api.get(
    route="/user_groups",
    response_models=[
        ResponseModel(
          model_schema=UserGroupsInResp,
          status_code=200,
          description="Success"
        )
    ],
    tags=["user_groups"]
)
def get_all_user_groups(
    offset: int = 0,
    limit: int = 10
):
    """
    Get all user groups in DB
    """
    user_groups = UserGroup.get_all_user_groups(
        offset,
        limit
    )
    count = UserGroup.get_all_user_groups_count()

    return UserGroupsInResp(
        user_groups=user_groups,
        total_count=count
    ), 200
