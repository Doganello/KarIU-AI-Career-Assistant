from __future__ import annotations

import requests
from typing import Any, Optional

from app.telegram_bot.config import BACKEND_URL, VACANCIES_LIMIT


class BackendError(Exception):
    pass


class ApiClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = BACKEND_URL

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, headers=self.headers, timeout=60, **kwargs)
        except requests.RequestException as exc:
            raise BackendError(f"Backend недоступен: {exc}") from exc

        if response.status_code >= 400:
            detail = ""
            try:
                detail = response.json().get("detail", "")
            except Exception:
                detail = response.text
            raise BackendError(f"Ошибка backend {response.status_code}: {detail}")

        if not response.content:
            return None
        return response.json()

    def login(self, email: str, password: str) -> dict[str, Any]:
        return self._request("POST", "/api/auth/login", json={"email": email, "password": password})

    def me(self) -> dict[str, Any]:
        return self._request("GET", "/api/auth/me")

    def profile(self) -> dict[str, Any]:
        return self._request("GET", "/api/resume/profile")

    def jobs(self, query: str | None = None, source: str | None = None, limit: int = VACANCIES_LIMIT) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit, "page": 1}
        if query:
            params["query"] = query
        if source:
            params["source"] = source
        return self._request("GET", "/api/jobs/", params=params)

    def job(self, vacancy_id: int) -> dict[str, Any]:
        return self._request("GET", f"/api/jobs/{vacancy_id}")

    def parse_kariu(self) -> dict[str, Any]:
        return self._request("POST", "/api/jobs/parse/kariu")

    def ai_chat(self, message: str, lang: str = "ru") -> str:
        data = self._request("POST", "/api/ai/chat", json={"message": message, "lang": lang})
        return data.get("response", "Нет ответа от AI")

    def vacancy_analysis(self, vacancy_text: str, lang: str = "ru") -> dict[str, Any]:
        return self._request("POST", "/api/ai/vacancy-analysis", json={"vacancy_text": vacancy_text, "lang": lang})

    def interview_start(self, interview_type: str, vacancy: str = "", difficulty: str = "medium", lang: str = "ru") -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/ai/interview/start",
            json={
                "interview_type": interview_type,
                "difficulty": difficulty,
                "vacancy": vacancy,
                "lang": lang,
            },
        )

    def interview_answer(self, session_id: str, answer: str) -> dict[str, Any]:
        return self._request("POST", "/api/ai/interview/answer", json={"session_id": session_id, "answer": answer})
