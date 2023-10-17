from typing import Optional

from odmantic.session import AIOSession

from app import crud, models
from app.schemas.item import ItemCreate
from app.testing.user import create_random_user, random_lower_string


async def create_random_item(
    db: AIOSession, *, owner: Optional[models.User] = None
) -> models.Item:
    if owner is None:
        owner = await create_random_user(db)
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return await crud.item.create_with_owner(db=db, obj_in=item_in, owner=owner)
