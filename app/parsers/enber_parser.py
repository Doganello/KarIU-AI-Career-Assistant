import requests
from bs4 import BeautifulSoup
from app.models.vacancy import Vacancy
from app import db
from datetime import datetime

class EnbekParser:
    BASE_URL = "https://www.enbek.kz/ru/search/vacancy"

    def run(self):
        """Запускается через Celery beat каждые 6 часов"""
        page = 1
        while True:
            vacancies = self._fetch_page(page)
            if not vacancies:
                break
            self._save(vacancies)
            page += 1

    def _fetch_page(self, page: int) -> list:
        resp = requests.get(self.BASE_URL, params={"page": page}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select(".vacancy-item")  # уточняется под реальный HTML

        result = []
        for card in cards:
            result.append({
                "title":       card.select_one(".vacancy-title").text.strip(),
                "company":     card.select_one(".company-name").text.strip(),
                "city":        card.select_one(".location").text.strip(),
                "source_url":  card.select_one("a")["href"],
                "source":      "enbek",
                "published_at": datetime.utcnow(),
            })
        return result

    def _save(self, data: list):
        for item in data:
            exists = Vacancy.query.filter_by(source_url=item["source_url"]).first()
            if not exists:
                db.session.add(Vacancy(**item))
        db.session.commit()