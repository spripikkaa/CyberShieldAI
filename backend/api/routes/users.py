import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies.database import require_mongo_connection
from backend.api.schemas.user import UserCreateRequest, UserLoginRequest, UserResponse
from backend.db.repositories.users import UserAlreadyExistsError, authenticate_user, create_user
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    payload: UserCreateRequest,
    _: None = Depends(require_mongo_connection),
) -> UserResponse:
    try:
        user = await create_user(payload.name, payload.email, payload.password)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except Exception:
        logger.exception("User registration failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register user.",
        ) from None

    return UserResponse(**user)


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate an existing user",
)
async def login_user(
    payload: UserLoginRequest,
    _: None = Depends(require_mongo_connection),
) -> UserResponse:
    user = await authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return UserResponse(**user)
