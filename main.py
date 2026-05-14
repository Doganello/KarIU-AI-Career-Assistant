from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.base import Base, engine
from app.api.router import router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables created!")
    logger.info(f"✅ CORS origins: {settings.CORS_ORIGINS}")
    yield


app = FastAPI(
    title="KarIU AI Career Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - максимально открытый для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://host.docker.internal:5173",
        "http://192.168.1.*:5173",  # Твой локальный IP
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
        "cors_origins": settings.CORS_ORIGINS
    }


@app.get("/health")
def health():
    return {"status": "healthy", "environment": "docker"}