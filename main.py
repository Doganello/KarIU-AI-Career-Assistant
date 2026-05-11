from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импорт настроек
from app.config import settings

# Импорт базы и моделей
from app.database.base import Base, engine
from app.models.user import User
from app.models.educational_program import EducationalProgram
from app.models.graduate import Graduate
from app.models.experience import Experience
from app.models.certificate import Certificate
from app.models.skill import GraduateSkill
from app.models.vacancy import Vacancy

from app.api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы!")
    print(f"✅ CORS origins: {settings.CORS_ORIGINS}")
    yield


app = FastAPI(
    title="KarIU AI Career Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =============================================

app.include_router(router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "cors_origins": settings.CORS_ORIGINS
    }