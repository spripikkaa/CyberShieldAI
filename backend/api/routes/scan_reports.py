import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.dependencies.database import require_mongo_connection
from backend.api.schemas.scan_report import ScanReportResponse
from backend.db.repositories.scan_reports import list_scan_reports_by_user
from backend.db.repositories.users import user_exists

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scan-reports", tags=["scan-reports"])


@router.get(
    "",
    response_model=list[ScanReportResponse],
    status_code=status.HTTP_200_OK,
    summary="List scan reports for a user",
)
async def get_scan_reports(
    user_id: str = Query(..., min_length=1, description="MongoDB user id."),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of reports to return."),
    _: None = Depends(require_mongo_connection),
) -> list[ScanReportResponse]:
    if not await user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' was not found.",
        )

    try:
        reports = await list_scan_reports_by_user(user_id, limit=limit)
    except Exception:
        logger.exception("Failed to fetch scan reports for user_id='%s'", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch scan reports.",
        ) from None

    return [ScanReportResponse(**report) for report in reports]
