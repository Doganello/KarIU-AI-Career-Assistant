from telegram import ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🔎 Вакансии", "🤖 ИИ чат"],
        ["💼 Кем я могу работать?", "📈 Какие навыки усилить?"],
        ["👤 Профиль", "ℹ️ Помощь"],
    ],
    resize_keyboard=True,
)


def auth_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [["🔐 Войти"], ["ℹ️ Помощь"]],
        resize_keyboard=True,
    )