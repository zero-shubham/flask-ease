from pydantic import BaseModel
from pydantic.main import ModelMetaclass


class ResponseModel(BaseModel):
    model_schema: ModelMetaclass
    status_code: int
    description: str

    class Config:
        arbitrary_types_allowed = True


class Form:

    def __init__(
        self,
        schema: ModelMetaclass,
        media_type: str = "application/x-www-form-urlencoded",
        min_length: int = None,
        max_length: int = None,
        regex: str = None
    ):
        self.schema = schema
        self.media_type = media_type
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex


class _OAuth2PasswordRequestFormSchema(BaseModel):
    username: str
    password: str
    grant_type: str
    client_id: str = ""
    client_secret: str = ""

    class Config:
        arbitrary_types_allowed = True


OAuth2PasswordRequestForm = Form(schema=_OAuth2PasswordRequestFormSchema)
