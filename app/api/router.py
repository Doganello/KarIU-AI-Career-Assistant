from fastapi import APIRouter
from app.api import auth, resume, jobs, ai_support

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(resume.router)
router.include_router(jobs.router)
router.include_router(ai_support.router)