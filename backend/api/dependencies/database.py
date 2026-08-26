from fastapi import HTTPException, status

from backend.db.connection import is_mongo_connected


def require_mongo_connection() -> None:
    if not is_mongo_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "MongoDB is unavailable. Start MongoDB and restart the backend, "
                "or check the MONGODB_URI environment variable."
            ),
        )
