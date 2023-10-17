from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from odmantic import Model as DBModel
from odmantic.session import AIOSession
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=DBModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model_cls: Type[ModelType]):
        self.model_cls = model_cls

    async def get(self, db: AIOSession, id: Any) -> Optional[ModelType]:
        return await db.find_one(self.model_cls, self.model_cls.id == id)

    async def get_multi(
        self, db: AIOSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        return await db.find(self.model_cls, skip=skip, limit=limit)

    async def create(self, db: AIOSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model_cls(**obj_in_data)
        await db.save(db_obj)
        return db_obj

    async def update(
        self,
        db: AIOSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        return await db.save(db_obj)

    async def remove(self, db: AIOSession, *, id: Any) -> ModelType:
        if not (obj := await db.find_one(self.model_cls, self.model_cls.id == id)):
            raise LookupError(id)
        await db.delete(obj)
        return obj
