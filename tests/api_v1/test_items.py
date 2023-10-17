from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from odmantic import ObjectId
from odmantic.session import AIOSession

from app import crud
from app.core.config import settings
from app.schemas.item import ItemCreate
from app.testing.item import create_random_item

_ITEMS = {"title": ["egg", "spam"], "description": ["abc", "fuzzbuzz"]}


@pytest.fixture
def many_items() -> list[dict]:
    return [dict(zip(_ITEMS.keys(), _)) for _ in zip(*_ITEMS.values())]  # type: ignore


@pytest.fixture
async def init_items(
    client: AsyncClient, db: AIOSession, many_items: list[dict], superuser_id: str
) -> AsyncGenerator[list[dict], None]:
    owner_id = ObjectId(superuser_id)
    owner = await crud.user.get(db, id=owner_id)
    assert owner

    created = []
    for data in many_items:
        item_in = ItemCreate(title=data["title"], description=data["description"])
        db_obj = await crud.item.create_with_owner(db, obj_in=item_in, owner=owner)
        created.append(db_obj)
    yield many_items
    for db_obj in created:
        await crud.item.remove(db, id=db_obj.id)


class TestRetrieveItems:
    url = f"{settings.API_V1_STR}/items/"

    async def test_empty(self, client: AsyncClient, superuser_token_headers: dict):
        resp = await client.get(self.url, headers=superuser_token_headers)
        assert resp.status_code == 200, resp.json()
        assert resp.json() == []

    async def test_retrieve_items(
        self,
        client: AsyncClient,
        superuser_token_headers: dict,
        superuser_id: str,
        init_items: list[dict],
    ):
        resp = await client.get(self.url, headers=superuser_token_headers)
        assert resp.status_code == 200, resp.json()
        all_items = resp.json()
        assert len(all_items) == len(init_items)

        expected = sorted(init_items, key=lambda item: item["title"])
        for i, item in enumerate(sorted(all_items, key=lambda item: item["title"])):
            assert item["title"] == expected[i]["title"]
            assert item["description"] == expected[i]["description"]
            assert item["owner_id"] == superuser_id


async def test_create_item(
    client: AsyncClient, db: AIOSession, superuser_token_headers: dict
):
    data = {"title": "Foo", "description": "Fighters"}
    response = await client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200, response.json()
    content = response.json()
    try:
        assert content["title"] == data["title"]
        assert content["description"] == data["description"]
        assert "id" in content
        assert "owner_id" in content
    finally:
        from app.models.item import Item

        obj_db = await db.find_one(
            Item, Item.title == data["title"], Item.description == data["description"]
        )
        if obj_db:
            await db.delete(obj_db)


async def test_read_item(
    client: AsyncClient, superuser_token_headers: dict, db: AIOSession
) -> None:
    item = await create_random_item(db)

    try:
        response = await client.get(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200, response.json()
        content = response.json()
        assert content["title"] == item.title
        assert content["description"] == item.description
        assert content["id"] == str(item.id)
        assert content["owner_id"] == str(item.owner.id)
    finally:
        await crud.item.remove(db, id=item.id)
        await crud.user.remove(db, id=item.owner.id)


async def test_delete_item(
    client: AsyncClient, superuser_token_headers: dict, db: AIOSession
) -> None:
    item = await create_random_item(db)

    item_read = None
    try:
        item_read = await crud.item.get(db, id=item.id)
        assert item_read

        response = await client.delete(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200, response.json()

        item_read = await crud.item.get(db, id=item.id)
        assert item_read is None
    finally:
        if item_read:
            await crud.item.remove(db, id=item_read.id)
        await crud.user.remove(db, id=item.owner.id)
