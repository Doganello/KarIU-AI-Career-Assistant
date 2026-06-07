import asyncio
import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.telegram_bot.handlers import (
    ai_chat_mode,
    career,
    handle_text,
    help_command,
    login,
    logout,
    parse_kariu,
    profile,
    skills,
    start,
    vacancies,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8964244726:AAEerjMsZPGnIbKmXxOZjYdGBpJqo7LEjL0"


def main() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("vacancies", vacancies))
    app.add_handler(CommandHandler("career", career))
    app.add_handler(CommandHandler("skills", skills))
    app.add_handler(CommandHandler("chat", ai_chat_mode))
    app.add_handler(CommandHandler("parse_kariu", parse_kariu))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("✅ BOT STARTED SUCCESSFULLY")

    app.run_polling(
        allowed_updates=["message"],
        stop_signals=None,
        close_loop=False,
    )


if __name__ == "__main__":
    main()