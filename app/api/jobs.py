from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.database.session import get_db
from app.models.vacancy import Vacancy
from app.schemas.vacancy import VacancyRead
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/", response_model=list[VacancyRead])
def list_vacancies(
        query: Optional[str] = Query(None),
        city: Optional[str] = Query(None),
        salary_from: Optional[int] = Query(None),
        work_format: Optional[str] = Query(None),
        industry: Optional[str] = Query(None),
        source: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        limit: int = Query(20, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Получение списка вакансий"""
    q = db.query(Vacancy).filter(Vacancy.is_active == True)

    if query:
        q = q.filter(
            or_(
                Vacancy.title.ilike(f"%{query}%"),
                Vacancy.company.ilike(f"%{query}%"),
            )
        )

    if city:
        q = q.filter(Vacancy.city.ilike(f"%{city}%"))

    if salary_from:
        q = q.filter(Vacancy.salary_from >= salary_from)

    if work_format:
        q = q.filter(Vacancy.work_format == work_format)

    if industry:
        q = q.filter(Vacancy.industry.ilike(f"%{industry}%"))

    if source:
        q = q.filter(Vacancy.source == source)

    offset = (page - 1) * limit
    vacancies = q.order_by(Vacancy.published_at.desc()).offset(offset).limit(limit).all()

    return vacancies


@router.get("/{vacancy_id}", response_model=VacancyRead)
def get_vacancy(
        vacancy_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """Получение конкретной вакансии по ID"""
    vacancy = db.query(Vacancy).get(vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return vacancy


@router.post("/parse/kariu")
def trigger_kariu_parse(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Добавление компаний-партнёров КарИУ"""
    from app.parsers.kariu_parser import KariuParser
    count = KariuParser().run()
    return {"message": f"Добавлено {count} компаний-партнёров"}