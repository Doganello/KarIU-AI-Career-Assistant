import requests
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INTERVIEW_TYPES = {
    "hr": "HR-интервью",
    "technical": "Техническое собеседование",
    "case": "Кейс-интервью"
}

LANG_MAP = {"ru": "русском", "kz": "казахском", "en": "английском"}


class InterviewSimulator:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = "deepseek-chat"
        self.history = []
        self.system = ""
        self.interview_type = ""
        self.question_count = 0
        self.max_questions = 6

    def start(self, interview_type: str, vacancy: str, graduate, lang: str = "ru") -> str:
        # Формируем контекст из профиля кандидата
        skills = ", ".join(s.name for s in graduate.skills) if graduate.skills else "не указаны"
        specialty = graduate.specialty if hasattr(graduate, 'specialty') and graduate.specialty else "не указана"
        exp_count = len(graduate.experiences) if graduate.experiences else 0

        # Формируем детальное описание опыта работы
        experience_text = ""
        if graduate.experiences and len(graduate.experiences) > 0:
            experience_text = "\n**Опыт работы кандидата:**\n"
            for exp in graduate.experiences:
                period = f"{exp.start_date or '?'} - {exp.end_date or 'настоящее время'}"
                experience_text += f"- {exp.company}: {exp.position} ({period})\n"
                if exp.description:
                    experience_text += f"  {exp.description}\n"

        # Личные качества
        personal_qualities = graduate.personal_qualities if hasattr(graduate,
                                                                    'personal_qualities') and graduate.personal_qualities else "не указаны"

        lang_label = LANG_MAP.get(lang, "русском")

        self.interview_type = interview_type
        self.question_count = 0

        self.system = f"""Ты опытный специалист по проведению собеседований. Сейчас ты проводишь {INTERVIEW_TYPES.get(interview_type, 'собеседование')} в IT-компании.

**ДАННЫЕ КАНДИДАТА:**
- Вакансия: {vacancy if vacancy else 'не указана'}
- Специальность: {specialty}
- Навыки: {skills}
- Личные качества: {personal_qualities}
{experience_text}
- Вуз: КарИУ
- Язык собеседования: {lang_label}

**ВАЖНО:** Используй информацию об опыте работы, навыках и личных качествах кандидата для составления релевантных вопросов. Задавай вопросы, которые проверяют реальные знания и опыт кандидата.

**ПРАВИЛА ПРОВЕДЕНИЯ СОБЕСЕДОВАНИЯ:**
1. Представься естественно (придумай имя и должность, подходящие к вакансии)
2. Задавай ТОЛЬКО ОДИН вопрос за раз
3. После ответа кандидата дай краткую обратную связь и задай следующий вопрос
4. Всего задай {self.max_questions} вопросов
5. Формат ответа: сначала обратная связь, потом следующий вопрос
6. После {self.max_questions}-го вопроса выдай ФИНАЛЬНЫЙ ОТЧЁТ:
   - Общая оценка
   - Сильные стороны
   - Зоны роста
   - Рекомендации по развитию
   - Вердикт

**ПЕРВЫЙ ШАГ:** Поприветствуй кандидата, представься и задай первый вопрос, учитывая опыт и навыки кандидата."""

        self.history = []
        return self._send_initial()

    def _send_initial(self) -> str:
        prompt = """Начни собеседование. Поприветствуй кандидата, представься и задай первый вопрос, учитывая его опыт, навыки и личные качества."""
        return self._send(prompt)

    def answer(self, user_answer: str) -> str:
        self.question_count += 1

        self.history.append({"role": "user", "content": user_answer})

        if self.question_count >= self.max_questions:
            prompt = f"""Это был {self.question_count}-й ответ кандидата. 
            Собеседование завершено. 
            Теперь выдай ФИНАЛЬНЫЙ ОТЧЁТ по формату выше.
            Не задавай больше вопросов, только отчёт."""
        else:
            prompt = f"""Кандидат ответил на {self.question_count}-й вопрос.
            Дай краткую обратную связь и задай следующий ({self.question_count + 1}-й) вопрос.
            Учитывай предыдущие ответы кандидата."""

        return self._send(prompt)

    def _send(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": self.system},
            *self.history,
            {"role": "user", "content": prompt}
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7,
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
                self.history.append({"role": "assistant", "content": reply})
                return reply
            else:
                logger.error(f"API Error: {response.status_code}")
                return "Извините, произошла ошибка. Попробуйте ещё раз."

        except Exception as e:
            logger.error(f"API Exception: {e}")
            return "Произошла ошибка. Попробуйте позже."