import logging
from typing import Literal

from bson import ObjectId
from bson.errors import InvalidId

from backend.db.config import SCAN_REPORTS_COLLECTION
from backend.db.connection import get_database
from backend.db.models.scan_report import ScanReportDocument
from backend.db.repositories.users import user_exists

logger = logging.getLogger(__name__)


def _serialize_scan_report(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "user_id": document["user_id"],
        "url": document["url"],
        "prediction": document["prediction"],
        "confidence": document["confidence"],
        "timestamp": document["timestamp"],
    }


async def create_scan_report(
    user_id: str,
    url: str,
    prediction: Literal["Legitimate", "Phishing"],
    confidence: float,
) -> dict | None:
    if not await user_exists(user_id):
        logger.warning("Scan report skipped: user_id '%s' was not found.", user_id)
        return None

    report = ScanReportDocument(
        user_id=user_id,
        url=url,
        prediction=prediction,
        confidence=confidence,
    )
    result = await get_database()[SCAN_REPORTS_COLLECTION].insert_one(report.to_mongo())
    created = await get_database()[SCAN_REPORTS_COLLECTION].find_one({"_id": result.inserted_id})
    if created is None:
        return None

    return _serialize_scan_report(created)


async def list_scan_reports_by_user(user_id: str, limit: int = 50) -> list[dict]:
    try:
        ObjectId(user_id)
    except InvalidId:
        return []

    cursor = (
        get_database()[SCAN_REPORTS_COLLECTION]
        .find({"user_id": user_id})
        .sort("timestamp", -1)
        .limit(limit)
    )
    documents = await cursor.to_list(length=limit)
    return [_serialize_scan_report(document) for document in documents]
