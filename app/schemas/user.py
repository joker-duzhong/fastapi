from typing import Optional

from pydantic import BaseModel, validator


# Shared properties
class UserBase(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    phone: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[str] = None

    @validator("id", pre=True, allow_reuse=True)
    def object_id2str(cls, v):
        return str(v)

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
