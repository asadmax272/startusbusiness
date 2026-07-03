from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, ai, auth, documents, notifications, orders, packages, payments, tickets
from app.core.config import settings
from app.core.security_headers import SecurityHeadersMiddleware

app = FastAPI(title=settings.app_name)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(packages.router)
app.include_router(ai.router)
app.include_router(payments.router)
app.include_router(orders.router)
app.include_router(documents.router)
app.include_router(tickets.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
