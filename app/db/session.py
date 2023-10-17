from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from app.core.config import settings

db_conf = settings.db.dict(include={"host", "port", "username", "password"})

client = AsyncIOMotorClient(
    **db_conf,
    authSource=settings.db.database,
    # https://pymongo.readthedocs.io/en/stable/examples/datetimes.html#reading-time
    tz_aware=True,
)

engine = AIOEngine(client=client, database=settings.db.database)
