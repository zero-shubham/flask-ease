from application import (
    Security,
    oauth2_scheme,
    HTTPException
)
import jwt
from core.jwt import (
    SECRET_KEY,
    ALGORITHM
)
from models.User import User
from schemas.auth import (
    Token
)


def get_current_user(token=Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = Token(**payload)

    except PyJWTError as e:
        if type(e) is ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired"
            )
        else:
            sentry_sdk.capture_exception(e)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials"
            )

    user = User.find_by_id(_id=token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
