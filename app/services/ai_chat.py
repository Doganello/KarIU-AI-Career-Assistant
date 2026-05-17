import requests
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPTS = {
    "ru": """Ты карьерный консультант КарИУ (Карагандинский индустриальный университет).

**ТВОЯ ЗАДАЧА:** Давать чёткие, структурированные ответы с правильным форматированием.

**ПРАВИЛА ФОРМАТИРОВАНИЯ (ОБЯЗАТЕЛЬНО К СОБЛЮДЕНИЮ):**

1. **Заголовки** оформляй так:
   **📌 Название раздела**

2. **Между разделами** ОБЯЗАТЕЛЬНО оставляй пустую строку

3. **Списки** делай так:
   - Первый пункт
   - Второй пункт
   - Третий пункт

4. **Нумерованные списки:**
   1. Первый шаг
   2. Второй шаг
   3. Третий шаг

5. **Важные вещи** выделяй **жирным**

6. **Код или команды** выделяй `вот так`

7. **Используй эмодзи:**
   📌 - для новых разделов
   💡 - для советов
   ✅ - для итогов
   ⚠️ - для важных предупреждений
   🎯 - для целей
   📊 - для примеров
   🔧 - для технических моментов

**ПРИМЕР ПРАВИЛЬНОГО ОТВЕТА:**

**📌 Как составить резюме**

---

**💡 Основные разделы:**

1. Шапка с контактами
2. Краткое описание
3. Опыт работы
4. Навыки
5. Образование

---

**✅ Итог:** Следуй этой структуре - получишь хорошее резюме.

---

Теперь отвечай на вопрос пользователя, строго соблюдая эти правила форматирования. Ответ должен быть читаемым, с отступами и эмодзи.""",

    "kz": """Сен КарИУ мансап кеңесшісің. Қазақша жауап бер. Форматтауды қатаң сақта: эмодзи, қалың шрифт, тізімдер, бос жолдар.""",

    "en": """You are a career consultant at KarIU. Answer in English. Strictly follow formatting: emojis, bold text, lists, empty lines between sections."""
}


class AIChat:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = "deepseek-chat"
        logger.info("AI Chat initialized with DeepSeek")

    def ask(self, message: str, graduate=None, lang: str = "ru") -> str:
        system = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["ru"])

        if graduate:
            system += f"\n\n**Контекст пользователя:**\n{self._build_profile_context(graduate, lang)}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": message}
            ],
            "max_tokens": 2000,
            "temperature": 0.5,  # Понизил температуру для более предсказуемого форматирования
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                reply = result['choices'][0]['message']['content']
                # Небольшая чистка на всякий случай
                reply = reply.replace('\\n\\n', '\n\n').replace('\\n', '\n')
                return reply
            else:
                logger.error(f"API Error: {response.status_code}")
                return "Извините, сервис временно недоступен. Попробуйте позже."

        except Exception as e:
            logger.error(f"API Exception: {e}")
            return "Произошла ошибка. Попробуйте ещё раз."

    def _build_profile_context(self, graduate, lang: str) -> str:
        skills = ", ".join(s.name for s in graduate.skills) if graduate.skills else "не указаны"
        specialty = graduate.specialty if hasattr(graduate, 'specialty') and graduate.specialty else "не указана"
        exp_count = len(graduate.experiences) if graduate.experiences else 0

        return f"""
- **Специальность:** {specialty}
- **Навыки:** {skills}
- **Опыт работы:** {exp_count} записей
- **Вуз:** КарИУ
"""