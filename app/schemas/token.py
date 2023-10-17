from typing import Optional

from odmantic import ObjectId
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[ObjectId] = None
