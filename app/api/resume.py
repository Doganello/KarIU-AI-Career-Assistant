from fastapi import APIRouter, Depends, HTTPException
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

router = APIRouter(prefix="/resume", tags=["Resume"])


# ── Профиль ───────────────────────────────────────────────────────

@router.get("/profile", response_model=GraduateRead)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return graduate


@router.put("/profile", response_model=GraduateRead)
def update_profile(
    data: GraduateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(graduate, field, value)
    db.commit()
    db.refresh(graduate)
    return graduate


# ── Опыт работы ───────────────────────────────────────────────────

@router.post("/experience", response_model=ExperienceRead, status_code=201)
def add_experience(
    data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
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
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    exp = db.query(Experience).filter_by(id=exp_id, graduate_id=graduate.id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.delete(exp)
    db.commit()


# ── Сертификаты ───────────────────────────────────────────────────

@router.post("/certificate", response_model=CertificateRead, status_code=201)
def add_certificate(
    data: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
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
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    cert = db.query(Certificate).filter_by(id=cert_id, graduate_id=graduate.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Сертификат не найден")
    db.delete(cert)
    db.commit()


# ── Навыки ────────────────────────────────────────────────────────

@router.post("/skill", response_model=SkillRead, status_code=201)
def add_skill(
    data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
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
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    skill = db.query(GraduateSkill).filter_by(id=skill_id, graduate_id=graduate.id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Навык не найден")
    db.delete(skill)
    db.commit()


# ── Генерация CV ──────────────────────────────────────────────────

@router.post("/generate")
def generate_cv(
    lang: str = "ru",
    target_vacancy: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    generator = CVGenerator()
    filename  = generator.generate(graduate, lang=lang, vacancy=target_vacancy)
    return {"download_url": f"/api/resume/download/{filename}"}


@router.get("/download/{filename}")
def download_cv(filename: str, current_user: User = Depends(get_current_user)):
    path = os.path.join("storage", "cvs", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path, filename=filename)


# ── Оценка CV ─────────────────────────────────────────────────────

@router.post("/score")
def score_cv(
    vacancy_text: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    scorer   = CVScorer()
    return scorer.evaluate(graduate, vacancy_text)