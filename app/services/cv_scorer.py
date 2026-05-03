import json
import re
import anthropic
from app.config import settings


class CVScorer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def evaluate(self, graduate, vacancy_text: str = "") -> dict:
        prompt = self._build_eval_prompt(graduate, vacancy_text)
        msg    = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_json(msg.content[0].text)

    def analyze_vacancy_fit(self, graduate, vacancy_text: str, lang: str = "ru") -> dict:
        prompt = self._build_fit_prompt(graduate, vacancy_text, lang)
        msg    = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_json(msg.content[0].text)

    def _build_eval_prompt(self, graduate, vacancy_text: str) -> str:
        skills = ", ".join(s.name for s in graduate.skills) if graduate.skills else "не указаны"
        return f"""
Ты эксперт по карьерному консультированию. Оцени резюме выпускника.

Профиль:
- Специальность: {graduate.program.name if graduate.program else 'не указана'}
- Опыт: {len(graduate.experiences)} записей
- Навыки: {skills}
- Сертификаты: {len(graduate.certificates)}
- Полнота профиля: {graduate.profile_completeness}%

Целевая вакансия: {vacancy_text or 'не указана'}

Ответь ТОЛЬКО в JSON без лишнего текста:
{{
  "score": <число 0-100>,
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "recommendations": ["...", "..."],
  "vacancy_match": <число 0-100 или null если вакансия не указана>
}}
"""

    def _build_fit_prompt(self, graduate, vacancy_text: str, lang: str) -> str:
        lang_map = {"ru": "русском", "kz": "казахском", "en": "английском"}
        skills   = ", ".join(s.name for s in graduate.skills) if graduate.skills else "—"
        return f"""
Ты HR-эксперт. Проанализируй соответствие кандидата вакансии.

Вакансия:
{vacancy_text}

Профиль кандидата:
- Навыки: {skills}
- Опыт работы: {len(graduate.experiences)} записей
- Образование: {graduate.program.name if graduate.program else '—'}

Ответь на {lang_map.get(lang, 'русском')} языке ТОЛЬКО в JSON:
{{
  "fit_score": <0-100>,
  "key_questions": ["вопрос1", "вопрос2", "вопрос3", "вопрос4", "вопрос5"],
  "readiness_level": "низкий | средний | высокий",
  "topics_to_prepare": ["тема1", "тема2"],
  "competence_gaps": ["пробел1", "пробел2"]
}}
"""

    def _parse_json(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"error": "Не удалось разобрать ответ AI"}
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {"error": "Некорректный JSON от AI"}