from typing import Optional

from odmantic import ObjectId
from pydantic import BaseModel, Field, validator

from .user import UserInDB


# Shared properties
class ItemBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: Optional[str] = None
    title: str
    owner: UserInDB

    @validator("id", pre=True, allow_reuse=True)
    def object_id2str(cls, v):
        return str(v)

    class Config:
        orm_mode = True


# Properties to return to client
class Item(ItemInDBBase):
    # workaround: owner_id from owner; use owner_id:str to replace owner:dict
    owner: UserInDB = Field(exclude=True)
    owner_id: str = ''

    @validator("owner_id", always=True)
    def populate_owner_id(cls, v, values):
        return str(values["owner"].id)

    class Config:
        orm_mode = True


# Properties stored in DB
class ItemInDB(ItemInDBBase):
    pass
