from pydantic import BaseModel


class LoginResp(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: str
    group: str


class Token(BaseModel):
    user_id: str
    group: str
    exp: int
    sub: str
