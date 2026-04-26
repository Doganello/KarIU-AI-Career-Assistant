import anthropic
from flask import current_app

INTERVIEW_TYPES = {
    "hr":        "HR-интервью (soft skills, мотивация, опыт)",
    "technical": "Техническое интервью по специальности",
    "case":      "Кейс-интервью (анализ ситуаций)",
}

class InterviewSimulator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])
        self.history = []

    def start(self, interview_type: str, vacancy: str, graduate) -> str:
        system = f"""
        Ты HR-специалист. Проводи {INTERVIEW_TYPES[interview_type]}.
        Вакансия: {vacancy}
        Задавай один вопрос за раз. После каждого ответа давай краткую оценку
        и задавай следующий вопрос. Всего 5-7 вопросов.
        В конце выдай финальный анализ в JSON:
        {{"overall": "...", "strengths": [...], "weaknesses": [...], "tips": [...]}}
        """
        self.history = []
        first_q = self._ask(system, "Начни интервью с приветствия и первого вопроса.")
        return first_q

    def answer(self, user_answer: str) -> str:
        self.history.append({"role": "user", "content": user_answer})
        response = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=800,
            messages=self.history
        )
        reply = response.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def _ask(self, system, prompt):
        msg = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        reply = msg.content[0].text
        self.history.append({"role": "assistant", "content": reply})
        return reply