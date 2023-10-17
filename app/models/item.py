from typing import Optional

from odmantic import Model, Reference

from .user import User  # noqa: F401


class Item(Model):
    title: str
    description: Optional[str]
    owner: User = Reference()

    class Config:
        collection = "item"
