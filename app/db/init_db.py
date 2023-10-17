from odmantic.session import AIOSession

from app import crud, schemas
from app.core.config import settings


async def init_db(db: AIOSession) -> None:
    if not await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER):
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.user.create(db, obj_in=user_in)  # noqa: F841
