from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.database.base import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # создаёт все таблицы при старте (для прода используй: alembic upgrade head)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="KarIU AI Career Assistant",
    description="Платформа поддержки трудоустройства студентов и выпускников КарИУ",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # в проде заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}