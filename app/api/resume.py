from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.graduate import Graduate
from app.models.experience import Experience
from app.models.certificate import Certificate
from app.models.skill import GraduateSkill
from app.schemas.graduate import GraduateCreate, GraduateRead
from app.schemas.experience import ExperienceCreate, ExperienceRead
from app.schemas.certificate import CertificateCreate, CertificateRead
from app.schemas.skill import SkillCreate, SkillRead
from app.utils.auth import get_current_user
from app.services.cv_generator import CVGenerator
from app.services.cv_scorer import CVScorer
import os
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume"])


# Profile endpoints
@router.get("/profile", response_model=GraduateRead)
def get_profile(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Get current user's graduate profile"""
    logger.info(f"Getting profile for user {current_user.id}")

    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        logger.error(f"Graduate not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Profile not found")

    logger.info(f"Profile found: {graduate.id}")
    return graduate


@router.put("/profile", response_model=GraduateRead)
def update_profile(
        data: GraduateCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Update current user's graduate profile"""
    logger.info(f"Updating profile for user {current_user.id}")
    logger.info(f"Received data: {data.model_dump()}")

    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        logger.error(f"Graduate not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(graduate, field, value)
            logger.info(f"Updated {field} = {value}")

    db.commit()
    db.refresh(graduate)

    logger.info(f"Profile updated successfully for graduate {graduate.id}")
    return graduate


@router.post("/profile", response_model=GraduateRead)
def create_or_update_profile(
        data: GraduateCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Create or update graduate profile (POST fallback)"""
    logger.info(f"POST profile for user {current_user.id}")

    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        # Create new profile
        graduate = Graduate(user_id=current_user.id)
        db.add(graduate)
        db.flush()

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(graduate, field, value)

    db.commit()
    db.refresh(graduate)

    return graduate


# Experience endpoints
@router.post("/experience", response_model=ExperienceRead, status_code=201)
def add_experience(
        data: ExperienceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Add work experience to profile"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    exp = Experience(**data.model_dump(), graduate_id=graduate.id)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/experience/{exp_id}", status_code=204)
def delete_experience(
        exp_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Delete work experience from profile"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    exp = db.query(Experience).filter_by(id=exp_id, graduate_id=graduate.id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")

    db.delete(exp)
    db.commit()


# Certificate endpoints
@router.post("/certificate", response_model=CertificateRead, status_code=201)
def add_certificate(
        data: CertificateCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Add certificate to profile"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    cert = Certificate(**data.model_dump(), graduate_id=graduate.id)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.delete("/certificate/{cert_id}", status_code=204)
def delete_certificate(
        cert_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Delete certificate from profile"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    cert = db.query(Certificate).filter_by(id=cert_id, graduate_id=graduate.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    db.delete(cert)
    db.commit()


# Skills endpoints
@router.post("/skill", response_model=SkillRead, status_code=201)
def add_skill(
        data: SkillCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Add skill to profile"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    skill = GraduateSkill(**data.model_dump(), graduate_id=graduate.id)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skill/{skill_id}", status_code=204)
def delete_skill(
        skill_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Delete skill from profile"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    skill = db.query(GraduateSkill).filter_by(id=skill_id, graduate_id=graduate.id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()


# CV Generation endpoints
@router.post("/generate")
def generate_cv(
        lang: str = "ru",
        target_vacancy: str = "",
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Generate CV document"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    generator = CVGenerator()
    filename = generator.generate(graduate, lang=lang, vacancy=target_vacancy)
    return {"download_url": f"/api/resume/download/{filename}"}


@router.get("/download/{filename}")
def download_cv(
        filename: str,
        current_user: User = Depends(get_current_user)
):
    """Download generated CV file"""
    path = os.path.join("storage", "cvs", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)


# CV Scoring endpoints
@router.post("/score")
def score_cv(
        vacancy_text: str = "",
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Score CV against vacancy"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    scorer = CVScorer()
    return scorer.evaluate(graduate, vacancy_text)