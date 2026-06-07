from contextlib import asynccontextmanager
import logging
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.base import Base, engine
from app.api.router import router
from app.telegram_bot.bot import main as telegram_bot_main


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_telegram_bot():
    try:
        logger.info("🚀 Starting Telegram bot...")
        telegram_bot_main()
    except Exception as e:
        logger.exception(f"❌ Telegram bot error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables created!")
    logger.info(f"✅ CORS origins: {settings.CORS_ORIGINS}")

    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Telegram bot thread started")

    yield


app = FastAPI(
    title="KarIU AI Career Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://host.docker.internal:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "telegram_bot": "started_in_main_py",
        "cors_origins": settings.CORS_ORIGINS,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": "docker",
        "telegram_bot": "enabled",
    }