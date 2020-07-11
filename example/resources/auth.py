from application import (
    my_api,
    ResponseModel,
    OAuth2PasswordRequestForm,
    Depends
)
from schemas.auth import (
    LoginResp,
    TokenPayload
)
from models.User import (
    User
)
from core.security import (
    verify_password
)
from core.jwt import (
    create_access_token
)


@my_api.post(
    route="/login",
    response_models=[
        ResponseModel(
          model_schema=LoginResp,
          status_code=200,
          description="Success"
        )
    ],
    tags=["authentication"]
)
def login(
    form_data: OAuth2PasswordRequestForm
):
    user_name = form_data.username
    password = form_data.password
    user_exists = User.find_by_user_name(user_name)
    if not user_exists:
        return {
            "detail": "User does not exists"
        }, 404

    password_matched = verify_password(
        password,
        user_exists.password
    )

    if not password_matched:
        return {
            "detail": "Incorrect credential combination"
        }, 401

    encoded_jwt, expire = create_access_token(data=TokenPayload(
        user_id=user_exists.id, group=user_exists.group).dict())

    return LoginResp(
        access_token=encoded_jwt.decode("utf-8"),
        token_type="bearer"
    ), 200
