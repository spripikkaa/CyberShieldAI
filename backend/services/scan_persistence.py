import logging
from typing import Literal

from backend.db.connection import is_mongo_connected
from backend.db.repositories.scan_reports import create_scan_report

logger = logging.getLogger(__name__)


async def persist_scan_report_if_connected(
    user_id: str,
    url: str,
    prediction: Literal["Legitimate", "Phishing"],
    confidence: float,
) -> None:
    if not is_mongo_connected():
        logger.debug("Skipping scan report persistence because MongoDB is not connected.")
        return

    try:
        await create_scan_report(user_id, url, prediction, confidence)
    except Exception:
        logger.exception(
            "Failed to persist scan report for user_id='%s' url='%s'",
            user_id,
            url,
        )
