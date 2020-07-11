from datetime import datetime, timedelta
import pytz

import jwt


ALGORITHM = "HS256"
access_token_jwt_subject = "access"
SECRET_KEY = "flask_ease_secret"


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow().replace(tzinfo=pytz.utc) + expires_delta
    else:
        expire = datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(hours=6)
    to_encode.update({"exp": expire, "sub": access_token_jwt_subject})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return (encoded_jwt, expire)
