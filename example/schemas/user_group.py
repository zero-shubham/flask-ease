from pydantic import BaseModel
from uuid import UUID
from typing import (
    List
)


class UserGroupBase(BaseModel):
    group: str


class UserGroupInDB(UserGroupBase):
    id: UUID


class UserGroupCreation(UserGroupBase):
    pass


class UserGroupInResp(UserGroupInDB):
    pass


class UserGroupsInResp(BaseModel):
    user_groups: List[UserGroupInResp]
    total_count: int
