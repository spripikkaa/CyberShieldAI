import asyncio
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from backend.api.routes.chatbot import router as chatbot_router
from backend.api.routes.dns import router as dns_router
from backend.api.routes.explain import router as explain_router
from backend.api.routes.predict import router as predict_router
from backend.api.routes.scan_reports import router as scan_reports_router
from backend.api.routes.ssl import router as ssl_router
from backend.api.routes.users import router as users_router
from backend.api.routes.whois import router as whois_router
from backend.db.connection import close_mongo_connection, connect_to_mongo
from backend.db.indexes import ensure_indexes
from backend.exceptions import FeatureMismatchError, model_not_loaded_message
from backend.ml.loader import load_phishing_model
from backend.chatbot.conversation_store import conversation_store

logger = logging.getLogger(__name__)


async def _periodic_chatbot_cleanup():
    """Purge idle chatbot conversations to prevent unbounded memory growth."""
    while True:
        await asyncio.sleep(60 * 30)
        try:
            removed = await conversation_store.cleanup_expired()
            if removed:
                logger.info(
                    "Chatbot cleanup removed %d idle conversation(s)",
                    removed,
                )
        except Exception:
            logger.exception("Error during chatbot conversation cleanup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the ML model once at startup so the first /predict request is fast.
    Logs a warning instead of crashing if the model file is not yet present.
    """
    try:
        load_phishing_model()
        logger.info("Phishing model loaded successfully.")
    except FileNotFoundError:
        logger.warning(model_not_loaded_message())
    except FeatureMismatchError:
        logger.exception("Feature schema mismatch detected at startup.")
        raise

    try:
        await connect_to_mongo()
        await ensure_indexes()
        logger.info("MongoDB connected and indexes ensured.")
    except Exception:
        logger.warning(
            "MongoDB is unavailable. URL scanning will continue, but user and "
            "scan-report features require a running MongoDB instance.",
            exc_info=True,
        )

    cleanup_task = asyncio.create_task(_periodic_chatbot_cleanup())

    yield

    cleanup_task.cancel()
    await close_mongo_connection()


app = FastAPI(
    title="CyberShield AI",
    description="Backend API for the CyberShield AI phishing detection project",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(FileNotFoundError)
async def model_file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Return 503 when inference is requested but the model file is missing."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": model_not_loaded_message()},
    )


@app.get("/")
def root():
    return {"message": "CyberShield AI Backend Running"}


app.include_router(predict_router)
app.include_router(explain_router)
app.include_router(whois_router)
app.include_router(ssl_router)
app.include_router(dns_router)
app.include_router(users_router)
app.include_router(scan_reports_router)
app.include_router(chatbot_router)
