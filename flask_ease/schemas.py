from pydantic import (
    BaseModel
)
from dataclasses import (
    dataclass
)
from pydantic.main import ModelMetaclass
from typing import Optional, Any


class ResponseModel(BaseModel):
    model_schema: Optional[ModelMetaclass]
    status_code: int
    description: str

    class Config:
        arbitrary_types_allowed = True


@dataclass
class Form:
    schema: ModelMetaclass
    media_type: str = "application/x-www-form-urlencoded"
    min_length: int = None
    max_length: int = None
    regex: str = None


@dataclass
class MultipartForm:
    schema: ModelMetaclass
    media_type: str = "multipart/form-data"
    min_length: int = None
    max_length: int = None


@dataclass
class File:
    mime_type: str
    max_length: int = None
    min_length: int = None
    _data: any = None


class _OAuth2PasswordRequestFormSchema(BaseModel):
    username: str
    password: str
    grant_type: str = ""
    client_id: str = ""
    client_secret: str = ""

    class Config:
        arbitrary_types_allowed = True


OAuth2PasswordRequestForm = Form(schema=_OAuth2PasswordRequestFormSchema)
