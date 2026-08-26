import logging

from backend.db.config import SCAN_REPORTS_COLLECTION, USERS_COLLECTION
from backend.db.connection import get_database

logger = logging.getLogger(__name__)


async def ensure_indexes() -> None:
    db = get_database()

    await db[USERS_COLLECTION].create_index("email", unique=True)
    await db[SCAN_REPORTS_COLLECTION].create_index("user_id")
    await db[SCAN_REPORTS_COLLECTION].create_index([("timestamp", -1)])

    logger.info(
        "MongoDB indexes ensured for '%s' and '%s'.",
        USERS_COLLECTION,
        SCAN_REPORTS_COLLECTION,
    )
