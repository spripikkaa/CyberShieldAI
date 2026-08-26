from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.chatbot import router as chatbot_router
from backend.api.routes.dns import router as dns_router
from backend.api.routes.explain import router as explain_router
from backend.api.routes.predict import router as predict_router
from backend.api.routes.scan_reports import router as scan_reports_router
from backend.api.routes.ssl import router as ssl_router
from backend.api.routes.users import router as users_router
from backend.api.routes.whois import router as whois_router


app = FastAPI(
    title="CyberShield AI",
    description="AI-based phishing website detection and cybersecurity assistant",
    version="1.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "CyberShield AI Backend Running Successfully"
    }


# API routers
app.include_router(predict_router)
app.include_router(chatbot_router)
app.include_router(dns_router)
app.include_router(explain_router)
app.include_router(scan_reports_router)
app.include_router(ssl_router)
app.include_router(users_router)
app.include_router(whois_router)