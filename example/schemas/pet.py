from pydantic import BaseModel, validator
from typing import List, Optional
from application import MultipartForm
from pydantic.dataclasses import dataclass
from uuid import UUID


class PetBase(BaseModel):
    name: str
    breed: str
    description: str
    owner: UUID


class PetInDB(PetBase):
    id: str


class PetInResp(PetInDB):
    pass


class PetsInResp(BaseModel):
    pets: List[PetInResp]
    count: int


class PetCreation(PetBase):
    attributes: Optional[List[str]]

    @validator("attributes", pre=True)
    def check_attributes(cls, v):
        if "," in v:
            v = v.split(",")
        else:
            v = [v]
        return v


PetCreationForm = MultipartForm(schema=PetCreation)
