import anthropic
from app.config import settings

INTERVIEW_TYPES = {
    "hr":        "HR-интервью (soft skills, мотивация, опыт работы)",
    "technical": "Техническое интервью по специальности кандидата",
    "case":      "Кейс-интервью (анализ бизнес-ситуаций)",
}

LANG_MAP = {"ru": "русском", "kz": "казахском", "en": "английском"}


class InterviewSimulator:
    def __init__(self):
        self.client  = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.history = []
        self.system  = ""

    def start(self, interview_type: str, vacancy: str, graduate, lang: str = "ru") -> str:
        skills    = ", ".join(s.name for s in graduate.skills) if graduate.skills else "—"
        lang_label = LANG_MAP.get(lang, "русском")

        self.system = f"""
Ты опытный HR-специалист. Проводи {INTERVIEW_TYPES.get(interview_type, 'интервью')}.
Вакансия: {vacancy or 'не указана'}
Специальность кандидата: {graduate.program.name if graduate.program else '—'}
Навыки кандидата: {skills}

Правила:
- Задавай ОДИН вопрос за раз
- После ответа кандидата: дай краткую оценку (1-2 предложения), затем следующий вопрос
- Всего 5-7 вопросов
- После последнего ответа выдай финальный анализ:

ФИНАЛЬНЫЙ АНАЛИЗ:
Общая оценка: <текст>
Сильные стороны: <список>
Зоны роста: <список>
Рекомендации: <список>

Веди интервью на {lang_label} языке.
"""
        self.history = []
        return self._send("Поприветствуй кандидата и задай первый вопрос.")

    def answer(self, user_answer: str) -> str:
        self.history.append({"role": "user", "content": user_answer})
        msg = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=self.system,
            messages=self.history,
        )
        reply = msg.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def _send(self, prompt: str) -> str:
        self.history.append({"role": "user", "content": prompt})
        msg = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            system=self.system,
            messages=self.history,
        )
        reply = msg.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        return reply