from typing import List

from fastapi.encoders import jsonable_encoder
from odmantic import ObjectId
from odmantic.session import AIOSession

from app.crud.base import CRUDBase
from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    async def create_with_owner(
        self, db: AIOSession, *, obj_in: ItemCreate, owner: User
    ) -> Item:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model_cls(**obj_in_data, owner=owner)
        return await db.save(db_obj)

    async def get_multi_by_owner(
        self, db: AIOSession, *, owner_id: ObjectId, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        raise NotImplementedError


item = CRUDItem(Item)
