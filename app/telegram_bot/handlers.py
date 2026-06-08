from __future__ import annotations

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.telegram_bot.api_client import ApiClient, BackendError
from app.telegram_bot.config import DEFAULT_LANG
from app.telegram_bot.formatters import chunks, profile_to_text, vacancy_to_text
from app.telegram_bot.keyboards import MAIN_MENU, auth_keyboard
from app.telegram_bot.storage import clear_session, get_session


HELP_TEXT = """
<b>ℹ️ Команды бота</b>

/start — открыть меню
/logout — выйти
/profile — показать профиль
/vacancies — вакансии партнёров КарИУ
/career — кем можно работать по твоей ОП
/skills — какие навыки усилить
/chat — ИИ чат
/parse_kariu — загрузить вакансии компаний-партнёров КарИУ

Авторизация:
1. Нажми «🔐 Войти»
2. Введи email
3. Следующим сообщением введи пароль
"""


def _client(update: Update) -> ApiClient:
    session = get_session(update.effective_user.id)
    return ApiClient(session.token)


def _is_authorized(update: Update) -> bool:
    return bool(get_session(update.effective_user.id).token)


def _clean_ai_text(text: str) -> str:
    return (
        text.replace("**", "")
        .replace("### ", "")
        .replace("## ", "")
        .replace("# ", "")
        .replace("```", "")
        .replace("|---|", "")
        .replace("|---", "")
    )


async def _send_long(update: Update, text: str, parse_mode=None) -> None:
    text = _clean_ai_text(text)

    for part in chunks(text):
        await update.effective_message.reply_text(
            part,
            disable_web_page_preview=True,
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_session(update.effective_user.id)
    session.waiting_for = None
    session.login_email = None

    if _is_authorized(update):
        await update.message.reply_text(
            "👋 Привет! Я карьерный Telegram-помощник КарИУ. Выбери действие:",
            reply_markup=MAIN_MENU,
        )
    else:
        await update.message.reply_text(
            "👋 Привет! Сначала нужно войти в аккаунт приложения.\n\n"
            "Нажми кнопку «🔐 Войти».",
            reply_markup=auth_keyboard(),
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=MAIN_MENU if _is_authorized(update) else auth_keyboard(),
    )


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_session(update.effective_user.id)
    session.waiting_for = "login_email"
    session.login_email = None

    await update.message.reply_text(
        "🔐 Вход в аккаунт\n\nВведите ваш email:",
        reply_markup=auth_keyboard(),
    )


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    clear_session(update.effective_user.id)
    await update.message.reply_text(
        "✅ Ты вышел из аккаунта.",
        reply_markup=auth_keyboard(),
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        await start(update, context)
        return

    try:
        data = _client(update).profile()
        await update.message.reply_text(
            profile_to_text(data),
            parse_mode=ParseMode.HTML,
            reply_markup=MAIN_MENU,
        )
    except BackendError as exc:
        await update.message.reply_text(f"⚠️ Ошибка получения профиля.\n{exc}")


async def vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        await start(update, context)
        return

    try:
        items = _client(update).jobs(source="kariu_partner")

        if not items:
            await update.message.reply_text(
                "Пока вакансии не найдены. Нажми /parse_kariu, чтобы загрузить предложения компаний-партнёров КарИУ.",
                reply_markup=MAIN_MENU,
            )
            return

        await update.message.reply_text(
            "🔎 Вакансии компаний-партнёров КарИУ:",
            reply_markup=MAIN_MENU,
        )

        for item in items:
            await update.message.reply_text(
                vacancy_to_text(item),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

    except BackendError as exc:
        await update.message.reply_text(f"⚠️ Ошибка загрузки вакансий.\n{exc}")


async def parse_kariu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        await start(update, context)
        return

    try:
        data = _client(update).parse_kariu()
        await update.message.reply_text(
            f"✅ {data.get('message', 'Парсинг выполнен')}",
            reply_markup=MAIN_MENU,
        )
    except BackendError as exc:
        await update.message.reply_text(f"⚠️ Ошибка парсинга.\n{exc}")


async def career(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        await start(update, context)
        return

    try:
        text = _client(update).ai_chat(
            "Кем я могу работать с моей образовательной программой? "
            "Дай список должностей, отраслей, стартовых позиций и план развития. "
            "Пиши обычным текстом для Telegram. "
            "Не используй Markdown, символы ** ## #, таблицы и HTML.",
            lang=DEFAULT_LANG,
        )
        await _send_long(update, text)
    except BackendError as exc:
        await update.message.reply_text(f"⚠️ Ошибка AI.\n{exc}")


async def skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        await start(update, context)
        return

    try:
        text = _client(update).ai_chat(
            "Какие навыки мне нужно усилить для трудоустройства? "
            "Учитывай мою образовательную программу, навыки и опыт. "
            "Дай конкретный план на 30 дней. "
            "Пиши обычным текстом для Telegram. "
            "Не используй Markdown, символы ** ## #, таблицы и HTML.",
            lang=DEFAULT_LANG,
        )
        await _send_long(update, text)
    except BackendError as exc:
        await update.message.reply_text(f"⚠️ Ошибка AI.\n{exc}")


async def ai_chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_authorized(update):
        await start(update, context)
        return

    session = get_session(update.effective_user.id)
    session.waiting_for = "ai_chat"

    await update.message.reply_text(
        "🤖 ИИ чат включён.\n\n"
        "Теперь напиши любой вопрос по карьере, резюме, навыкам, вакансиям или трудоустройству.\n\n"
        "Чтобы выйти из ИИ чата, нажми /start.",
        reply_markup=MAIN_MENU,
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    session = get_session(update.effective_user.id)

    button_map = {
        "🔐 Войти": "login",
        "🔎 Вакансии": "vacancies",
        "🤖 ИИ чат": "ai_chat",
        "💼 Кем я могу работать?": "career",
        "📈 Какие навыки усилить?": "skills",
        "👤 Профиль": "profile",
        "ℹ️ Помощь": "help",
    }

    action = button_map.get(text)

    if action == "login":
        await login(update, context)
        return

    if session.waiting_for == "login_email":
        session.login_email = text
        session.waiting_for = "login_password"

        await update.message.reply_text(
            "✅ Email принят.\n\nТеперь введите пароль:",
            reply_markup=auth_keyboard(),
        )
        return

    if session.waiting_for == "login_password":
        email = session.login_email
        password = text

        if not email:
            session.waiting_for = "login_email"
            await update.message.reply_text("Введите email ещё раз:")
            return

        try:
            data = ApiClient().login(email, password)
            session.token = data["access_token"]
            session.waiting_for = None
            session.login_email = None

            await update.message.reply_text(
                "✅ Вход выполнен. Теперь можно пользоваться ботом.",
                reply_markup=MAIN_MENU,
            )

        except BackendError as exc:
            session.waiting_for = "login_email"
            session.login_email = None

            await update.message.reply_text(
                f"⚠️ Не удалось войти.\n{exc}\n\n"
                "Попробуем ещё раз. Введите email:",
                reply_markup=auth_keyboard(),
            )

        return

    if action == "vacancies":
        await vacancies(update, context)
        return

    if action == "ai_chat":
        await ai_chat_mode(update, context)
        return

    if action == "career":
        await career(update, context)
        return

    if action == "skills":
        await skills(update, context)
        return

    if action == "profile":
        await profile(update, context)
        return

    if action == "help":
        await help_command(update, context)
        return

    if not _is_authorized(update):
        await start(update, context)
        return

    if session.waiting_for == "ai_chat":
        try:
            response = _client(update).ai_chat(
                text + "\n\nПиши обычным текстом для Telegram. Не используй Markdown, символы ** ## #, таблицы и HTML.",
                lang=DEFAULT_LANG,
            )
            await _send_long(update, response)
        except BackendError as exc:
            await update.message.reply_text(f"⚠️ Ошибка AI.\n{exc}")
        return

    await update.message.reply_text(
        "Выбери действие через кнопки меню 👇",
        reply_markup=MAIN_MENU,
    )