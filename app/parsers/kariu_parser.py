import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app.database.session import SessionLocal
from app.models.vacancy import Vacancy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KariuParser:
    """Парсер вакансий с сайта КарИУ и компаний-партнёров"""

    # Компании-партнёры с ссылками на вакансии
    PARTNER_COMPANIES = [
        {
            "name": "ТОО «Корпорация КазЭнергоМаш»",
            "url": "https://docs.google.com/document/d/1YfRusmQiHJDgI0ioo64yH3bKUv_qLwI4/edit",
            "source": "kariu_partner"
        },
        {
            "name": "ТОО «Карагандинский фармацевтический комплекс»",
            "url": "https://drive.google.com/file/d/1CesQJCiYVqOOItY5u9Z_ganXt1zr4v87/view",
            "source": "kariu_partner"
        },
        {
            "name": "ТОО «Караганды Жарык»",
            "url": "https://drive.google.com/file/d/1iNdp48Al_ZuTFv_EpHL8UyBqP3gyI4BP/view",
            "source": "kariu_partner"
        },
        {
            "name": "ТОО «Караганда Энергоцентр»",
            "url": "https://drive.google.com/file/d/1z7QNfb7ROQkIDqIDB1Ya1xQ2TAbUNYRm/view",
            "source": "kariu_partner"
        },
        {
            "name": "ГКП «Талдыкорганский индустриальный колледж»",
            "url": "https://drive.google.com/file/d/1zM5yeB2EYd4abeUrtaE5EGLenvIG8w3B/view",
            "source": "kariu_partner"
        },
        {
            "name": "ERASIAN MACHINERY",
            "url": "https://drive.google.com/file/d/15oVVhxJoGQazHWMJ3eMnf1taVVzWjPIx/view",
            "source": "kariu_partner"
        },
        {
            "name": "ТОО «КМК Trade Company»",
            "url": "https://docs.google.com/document/d/1PzeqdNMvGXm_Jne9SZVju75B9DrhxFog/edit",
            "source": "kariu_partner"
        },
        {
            "name": "Linde",
            "url": "https://drive.google.com/file/d/1n8xSyfr8FBxWZMi3f78rbi_jl_9sVaEo/view",
            "source": "kariu_partner"
        },
        {
            "name": "AsiarT",
            "url": "https://drive.google.com/file/d/1BmTFnkChZ6Ps3hVybpSrFBS2jNGIkXuh/view",
            "source": "kariu_partner"
        },
        {
            "name": "АО «Централ Азия Цемент»",
            "url": "https://docs.google.com/document/d/1G92meYPq8gav8EsUWAmc9dIThaebGqfB/edit",
            "source": "kariu_partner"
        },
        {
            "name": "Институт судебных экспертиз по Карагандинской области",
            "url": "",
            "source": "kariu_partner"
        }
    ]

    def run(self) -> int:
        """Запуск парсинга вакансий компаний-партнёров"""
        count = 0
        for company in self.PARTNER_COMPANIES:
            if company["url"]:
                vacancy = self._create_vacancy_from_company(company)
                if self._save_vacancy(vacancy):
                    count += 1
                    logger.info(f"✅ Добавлена вакансия: {company['name']}")
            else:
                logger.warning(f"⚠️ Нет ссылки для компании: {company['name']}")

        logger.info(f"📊 Всего добавлено вакансий: {count}")
        return count

    def _create_vacancy_from_company(self, company: dict) -> Vacancy:
        """Создание объекта вакансии из данных компании"""
        return Vacancy(
            title=f"Вакансии в компании {company['name']}",
            company=company['name'],
            description=f"Актуальные вакансии в компании {company['name']}. Подробности по ссылке.",
            source_url=company['url'],
            source=company['source'],
            published_at=datetime.now(),
            is_active=True
        )

    def _save_vacancy(self, vacancy: Vacancy) -> bool:
        """Сохранение вакансии в БД"""
        db = SessionLocal()
        try:
            # Проверяем, существует ли уже такая вакансия
            existing = db.query(Vacancy).filter_by(
                company=vacancy.company,
                source_url=vacancy.source_url
            ).first()

            if existing:
                logger.info(f"Вакансия уже существует: {vacancy.company}")
                return False

            db.add(vacancy)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
            db.rollback()
            return False
        finally:
            db.close()