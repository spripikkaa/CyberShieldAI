from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from backend.core.security import hash_password, verify_password
from backend.db.config import USERS_COLLECTION
from backend.db.connection import get_database
from backend.db.models.user import UserDocument


class UserAlreadyExistsError(Exception):
    """Raised when registering a user with an email that already exists."""


class UserNotFoundError(Exception):
    """Raised when a user id does not exist in MongoDB."""


def _serialize_user(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "name": document["name"],
        "email": document["email"],
        "created_at": document["created_at"],
    }


async def create_user(name: str, email: str, password: str) -> dict:
    user = UserDocument(
        name=name.strip(),
        email=email.strip().lower(),
        hashed_password=hash_password(password),
    )

    try:
        result = await get_database()[USERS_COLLECTION].insert_one(user.to_mongo())
    except DuplicateKeyError as exc:
        raise UserAlreadyExistsError(f"A user with email '{email}' already exists.") from exc

    created = await get_database()[USERS_COLLECTION].find_one({"_id": result.inserted_id})
    if created is None:
        raise RuntimeError("Failed to load user after creation.")

    return _serialize_user(created)


async def get_user_by_email(email: str) -> dict | None:
    document = await get_database()[USERS_COLLECTION].find_one(
        {"email": email.strip().lower()}
    )
    if document is None:
        return None

    return _serialize_user(document)


async def authenticate_user(email: str, password: str) -> dict | None:
    document = await get_database()[USERS_COLLECTION].find_one(
        {"email": email.strip().lower()}
    )
    if document is None:
        return None

    if not verify_password(password, document["hashed_password"]):
        return None

    return _serialize_user(document)


async def get_user_by_id(user_id: str) -> dict | None:
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return None

    document = await get_database()[USERS_COLLECTION].find_one({"_id": object_id})
    if document is None:
        return None

    return _serialize_user(document)


async def user_exists(user_id: str) -> bool:
    return await get_user_by_id(user_id) is not None
