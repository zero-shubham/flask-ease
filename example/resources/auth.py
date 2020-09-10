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
from crud.user import (
    find_user_by_user_name
)
from core.security import (
    verify_password
)
from core.jwt import (
    create_access_token
)


@my_api.post(
    route="/login",
    response_model=LoginResp,
    tags=["authentication"]
)
def login(
    form_data: OAuth2PasswordRequestForm
):
    user_name = form_data.username
    password = form_data.password
    user_exists = find_user_by_user_name(user_name)
    if not user_exists:
        return {
            "detail": "User does not exists"
        }, 404

    password_matched = verify_password(
        password,
        user_exists["password"]
    )

    if not password_matched:
        return {
            "detail": "Incorrect credential combination"
        }, 401

    encoded_jwt, expire = create_access_token(
        data=TokenPayload(user_id=user_exists["id"]).dict()
    )

    return LoginResp(
        access_token=encoded_jwt.decode("utf-8"),
        token_type="bearer"
    ), 200
