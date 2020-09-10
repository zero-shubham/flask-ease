from pydantic import (
    BaseModel
)
from enum import Enum
from uuid import UUID
from typing import (
    List
)


class UserBase(BaseModel):
    email: str
    password: str


class UserInDB(UserBase):
    id: UUID


class UserInResp(UserInDB):
    pass


class UsersInResp(BaseModel):
    users: List[UserInResp]
    total_count: int


class UserCreation(UserBase):
    pass
