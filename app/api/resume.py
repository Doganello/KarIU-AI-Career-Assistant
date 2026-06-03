from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.graduate import Graduate
from app.models.experience import Experience
from app.models.certificate import Certificate
from app.models.skill import GraduateSkill
from app.models.educational_program import EducationalProgram
from app.schemas.graduate import GraduateCreate, GraduateRead
from app.schemas.experience import ExperienceCreate, ExperienceRead
from app.schemas.certificate import CertificateCreate, CertificateRead
from app.schemas.skill import SkillCreate, SkillRead
from app.utils.auth import get_current_user
from app.services.cv_generator import CVGenerator
from app.services.cv_scorer import CVScorer
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume"])


# ── Образовательные программы ─────────────────────────────────────

@router.get("/educational-programs")
def get_educational_programs(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Get all educational programs"""
    programs = db.query(EducationalProgram).order_by(EducationalProgram.id).all()
    return [{"id": p.id, "code": p.code, "name": p.name} for p in programs]


# ── Профиль ───────────────────────────────────────────────────────

@router.get("/profile", response_model=GraduateRead)
def get_profile(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Get current user's graduate profile"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")
    return graduate


@router.put("/profile", response_model=GraduateRead)
def update_profile(
        data: GraduateCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Update current user's graduate profile with experiences and skills"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = data.model_dump(exclude_unset=True, exclude={'experiences', 'certificates', 'skills'})
    for field, value in update_data.items():
        setattr(graduate, field, value)
        logger.info(f"Updated {field} = {value}")

    if 'experiences' in data.model_dump(exclude_unset=True):
        for exp in graduate.experiences[:]:
            db.delete(exp)
        for exp_data in data.experiences:
            if exp_data.company and exp_data.position:
                new_exp = Experience(
                    graduate_id=graduate.id,
                    company=exp_data.company,
                    position=exp_data.position,
                    description=exp_data.description,
                    start_date=exp_data.start_date,
                    end_date=exp_data.end_date if exp_data.end_date else None,
                    is_internship=exp_data.is_internship
                )
                db.add(new_exp)

    if 'certificates' in data.model_dump(exclude_unset=True):
        for cert in graduate.certificates[:]:
            db.delete(cert)
        for cert_data in data.certificates:
            if cert_data.title:
                new_cert = Certificate(
                    graduate_id=graduate.id,
                    title=cert_data.title,
                    issuer=cert_data.issuer,
                    issued_date=cert_data.issued_date,
                    url=cert_data.url
                )
                db.add(new_cert)

    if 'skills' in data.model_dump(exclude_unset=True):
        for skill in graduate.skills[:]:
            db.delete(skill)
        for skill_data in data.skills:
            if skill_data.name:
                new_skill = GraduateSkill(
                    graduate_id=graduate.id,
                    name=skill_data.name[:500],
                    level=skill_data.level
                )
                db.add(new_skill)

    db.commit()
    db.refresh(graduate)
    return graduate


@router.post("/profile", response_model=GraduateRead)
def create_or_update_profile(
        data: GraduateCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Create or update graduate profile (POST fallback)"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        graduate = Graduate(user_id=current_user.id)
        db.add(graduate)
        db.flush()

    update_data = data.model_dump(exclude_unset=True, exclude={'experiences', 'certificates', 'skills'})
    for field, value in update_data.items():
        setattr(graduate, field, value)

    if 'experiences' in data.model_dump(exclude_unset=True):
        for exp in graduate.experiences[:]:
            db.delete(exp)
        for exp_data in data.experiences:
            if exp_data.company and exp_data.position:
                new_exp = Experience(
                    graduate_id=graduate.id,
                    company=exp_data.company,
                    position=exp_data.position,
                    description=exp_data.description,
                    start_date=exp_data.start_date,
                    end_date=exp_data.end_date if exp_data.end_date else None,
                    is_internship=exp_data.is_internship
                )
                db.add(new_exp)

    if 'certificates' in data.model_dump(exclude_unset=True):
        for cert in graduate.certificates[:]:
            db.delete(cert)
        for cert_data in data.certificates:
            if cert_data.title:
                new_cert = Certificate(
                    graduate_id=graduate.id,
                    title=cert_data.title,
                    issuer=cert_data.issuer,
                    issued_date=cert_data.issued_date,
                    url=cert_data.url
                )
                db.add(new_cert)

    if 'skills' in data.model_dump(exclude_unset=True):
        for skill in graduate.skills[:]:
            db.delete(skill)
        for skill_data in data.skills:
            if skill_data.name:
                new_skill = GraduateSkill(
                    graduate_id=graduate.id,
                    name=skill_data.name[:500],
                    level=skill_data.level
                )
                db.add(new_skill)

    db.commit()
    db.refresh(graduate)
    return graduate


# ── Генерация CV ──────────────────────────────────────────────────

@router.post("/generate-cv")
def generate_cv(
        lang: str = "ru",
        target_vacancy: str = "",
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Generate CV document in DOCX format"""
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Profile not found")

    generator = CVGenerator()
    filename = generator.generate(graduate, lang=lang, vacancy=target_vacancy)

    return {"download_url": f"/api/resume/download-cv/{filename}"}


@router.get("/download-cv/{filename}")
def download_cv(
        filename: str,
        current_user: User = Depends(get_current_user),
):
    """Download generated CV file"""
    filepath = os.path.join("storage", "cvs", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )


# ── Опыт работы (отдельные эндпоинты) ─────────────────────────────

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


# ── Сертификаты ───────────────────────────────────────────────────

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


# ── Навыки (отдельные эндпоинты) ─────────────────────────────────

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


# ── Оценка CV ─────────────────────────────────────────────────────

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