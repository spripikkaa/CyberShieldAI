import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.db.config import MONGODB_DB_NAME, MONGODB_URI

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


def is_mongo_connected() -> bool:
    return _database is not None


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("MongoDB is not connected.")
    return _database


async def connect_to_mongo() -> None:
    global _client, _database

    _client = AsyncIOMotorClient(MONGODB_URI)
    _database = _client[MONGODB_DB_NAME]
    await _client.admin.command("ping")
    logger.info("Connected to MongoDB database '%s'.", MONGODB_DB_NAME)


async def close_mongo_connection() -> None:
    global _client, _database

    if _client is not None:
        _client.close()
        logger.info("MongoDB connection closed.")

    _client = None
    _database = None
