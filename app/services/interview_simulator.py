import requests
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterviewSimulator:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = "deepseek-chat"
        self.history = []
        self.question_count = 0
        self.max_questions = 6
        self.candidate_name = ""
        self.vacancy = ""

    def start(self, interview_type: str, difficulty: str, vacancy: str, graduate, lang: str = "ru") -> str:
        self.vacancy = vacancy if vacancy else "специалист"
        self.candidate_name = graduate.first_name if hasattr(graduate,
                                                             'first_name') and graduate.first_name else "кандидат"

        skills = ", ".join([s.name for s in graduate.skills]) if graduate.skills else "не указаны"
        exp_text = ""
        if graduate.experiences:
            for exp in graduate.experiences:
                exp_text += f"- {exp.position} в {exp.company}\n"
        if not exp_text:
            exp_text = "нет"

        specialty = graduate.specialty if hasattr(graduate, 'specialty') and graduate.specialty else "не указана"

        self.question_count = 0
        self.history = []

        system = f"""Ты проводишь собеседование на должность: {self.vacancy}.

Кандидат: {self.candidate_name}
Образование: {specialty}
Навыки: {skills}
Опыт: {exp_text}

ПРАВИЛА:
1. Задавай вопросы ТОЛЬКО про {self.vacancy}
2. Всего задай {self.max_questions} вопросов
3. После ответа дай короткую обратную связь
4. После 6-го вопроса напиши "ФИНАЛЬНЫЙ ОТЧЁТ:"

Начни с приветствия и задай первый вопрос про {self.vacancy}."""

        return self._send(system, "start")

    def answer(self, user_answer: str) -> str:
        self.question_count += 1
        self.history.append({"role": "user", "content": user_answer})

        if self.question_count >= self.max_questions:
            prompt = f"""Это был последний вопрос.
Напиши "ФИНАЛЬНЫЙ ОТЧЁТ:" и короткую оценку кандидата.
Не задавай больше вопросов."""
        else:
            prompt = f"""Дай короткую обратную связь (1 предложение).
Затем задай следующий вопрос про {self.vacancy}."""

        return self._send(None, prompt)

    def _send(self, system: str, prompt: str) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(self.history)
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.5,
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            result = response.json()
            reply = result['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            logger.error(f"API Error: {e}")
            return "Ошибка."