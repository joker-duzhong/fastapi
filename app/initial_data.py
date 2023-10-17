from app.db.init_db import init_db
from app.db.session import engine
from app.utilities.logging import get_logger

logger = get_logger(__name__)


async def init() -> None:
    async with engine.session() as session:
        await init_db(session)


async def main() -> None:
    logger.info("Creating initial data")
    await init()
    logger.info("Initial data created")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
