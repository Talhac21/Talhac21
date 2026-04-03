import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.db.session import Base, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: validate encryption key and create tables
    from cryptography.fernet import Fernet, InvalidToken

    try:
        Fernet(settings.session_encryption_key.encode())
    except (ValueError, InvalidToken) as exc:
        raise SystemExit(
            f"Invalid SESSION_ENCRYPTION_KEY – must be a valid Fernet key: {exc}"
        ) from exc

    Base.metadata.create_all(bind=engine)
    logger.info("RR Control Panel API started")
    yield


app = FastAPI(title="RR Control Panel API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
