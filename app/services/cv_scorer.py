import anthropic
from flask import current_app


class CVScorer:
    def evaluate(self, graduate, vacancy_text: str) -> dict:
        client = anthropic.Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])

        prompt = self._build_prompt(graduate, vacancy_text)
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_response(message.content[0].text)

    def _build_prompt(self, graduate, vacancy_text):
        return f"""
        Оцени резюме выпускника и дай рекомендации.

        Профиль:
        - Специальность: {graduate.program.name if graduate.program else '—'}
        - Опыт: {graduate.experiences.count()} записей
        - Навыки: {[s.name for s in graduate.skills]}

        Вакансия (если есть): {vacancy_text}

        Ответь строго в JSON:
        {{
          "score": <0-100>,
          "strengths": ["..."],
          "weaknesses": ["..."],
          "recommendations": ["..."]
        }}
        """

    def _parse_response(self, text: str) -> dict:
        import json, re
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group()) if match else {}