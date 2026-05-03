from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.session import get_db
from app.models.user import User
from app.models.graduate import Graduate
from app.utils.auth import get_current_user
from app.services.ai_chat import AIChat
from app.services.interview_simulator import InterviewSimulator
from app.services.cv_scorer import CVScorer

router = APIRouter(prefix="/ai", tags=["AI Support"])

_interview_sessions: dict[str, InterviewSimulator] = {}


class ChatMessage(BaseModel):
    message: str
    lang:    str = "ru"


class InterviewStart(BaseModel):
    interview_type: str
    vacancy:        str = ""
    lang:           str = "ru"


class InterviewAnswer(BaseModel):
    session_id: str
    answer:     str


class VacancyAnalysis(BaseModel):
    vacancy_text: str
    lang:         str = "ru"


@router.post("/chat")
def chat(
    body: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    response = AIChat().ask(body.message, graduate=graduate, lang=body.lang)
    return {"response": response}


@router.post("/interview/start")
def start_interview(
    body: InterviewStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate  = db.query(Graduate).filter_by(user_id=current_user.id).first()
    simulator = InterviewSimulator()
    first_q   = simulator.start(
        interview_type=body.interview_type,
        vacancy=body.vacancy,
        graduate=graduate,
        lang=body.lang,
    )
    session_id = f"{current_user.id}_{body.interview_type}"
    _interview_sessions[session_id] = simulator
    return {"session_id": session_id, "question": first_q}


@router.post("/interview/answer")
def answer_interview(body: InterviewAnswer):
    simulator = _interview_sessions.get(body.session_id)
    if not simulator:
        raise HTTPException(status_code=404, detail="Сессия не найдена или истекла")
    return {"response": simulator.answer(body.answer)}


@router.post("/vacancy-analysis")
def analyze_vacancy(
    body: VacancyAnalysis,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = db.query(Graduate).filter_by(user_id=current_user.id).first()
    return CVScorer().analyze_vacancy_fit(graduate, body.vacancy_text, lang=body.lang)