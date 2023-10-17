from typing import Any, Dict, Optional, Union

from odmantic.session import AIOSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(
        self, db: AIOSession, *, email: str
    ) -> Optional[User]:  # noqa
        return await db.find_one(User, User.email == email)

    async def create(self, db: AIOSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        return await db.save(db_obj)

    async def update(
        self, db: AIOSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AIOSession, *, email: str, password: str
    ) -> Optional[User]:
        if not (_user := await self.get_by_email(db, email=email)):
            return None
        if not verify_password(password, _user.hashed_password):
            return None
        return _user

    def is_active(self, user: User) -> bool:  # noqa
        return user.is_active

    def is_superuser(self, user: User) -> bool:  # noqa
        return user.is_superuser


user = CRUDUser(User)
