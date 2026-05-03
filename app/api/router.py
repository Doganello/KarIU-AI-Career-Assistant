from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.resume import router as resume_router
from app.api.jobs import router as jobs_router
from app.api.ai_support import router as ai_router

router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(resume_router)
router.include_router(jobs_router)
router.include_router(ai_router)