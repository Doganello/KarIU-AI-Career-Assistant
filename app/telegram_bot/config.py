from app.config import settings


TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
BACKEND_URL = settings.BACKEND_URL.rstrip("/")
DEFAULT_LANG = settings.BOT_DEFAULT_LANG
VACANCIES_LIMIT = settings.BOT_VACANCIES_LIMIT