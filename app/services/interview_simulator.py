import requests
import logging
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LANG_MAP = {"ru": "Русский", "kz": "Қазақша", "en": "English"}


class InterviewSimulator:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = "deepseek-chat"
        self.history = []
        self.question_count = 0
        self.max_questions = 5
        self.candidate_name = ""
        self.vacancy = ""

    def start(self, interview_type: str, difficulty: str, vacancy: str, graduate, lang: str = "ru") -> str:
        self.vacancy = vacancy if vacancy else "специалист"
        self.candidate_name = graduate.first_name if hasattr(graduate,
                                                             'first_name') and graduate.first_name else "кандидат"

        # Собираем реальные данные кандидата
        skills = ", ".join([s.name for s in graduate.skills]) if graduate.skills else "не указаны"
        exp_count = len(graduate.experiences) if graduate.experiences else 0

        exp_text = ""
        if exp_count > 0:
            exp_text = "Опыт работы:\n"
            for exp in graduate.experiences:
                exp_text += f"- {exp.position} в {exp.company}"
                if exp.start_date:
                    exp_text += f" ({exp.start_date}"
                    if exp.end_date:
                        exp_text += f" - {exp.end_date}"
                    exp_text += ")"
                exp_text += "\n"
        else:
            exp_text = "Опыт работы: нет"

        personal = graduate.personal_qualities if hasattr(graduate,
                                                          'personal_qualities') and graduate.personal_qualities else "не указаны"
        specialty = graduate.specialty if hasattr(graduate, 'specialty') and graduate.specialty else "не указана"

        # Определяем должность интервьюера в зависимости от вакансии и типа собеседования
        interviewer_role = self._get_interviewer_role(self.vacancy, interview_type)

        # Тип собеседования
        type_desc = {
            "hr": f"HR-интервью. Спрашивай про мотивацию, карьерные цели, работу в команде, стрессоустойчивость.",
            "technical": f"Техническое собеседование на {self.vacancy}. Спрашивай про профессиональные навыки, технологии, конкретные задачи.",
            "case": f"Кейс-интервью. Дай гипотетическую ситуацию по {self.vacancy} и спроси как кандидат будет действовать."
        }

        self.question_count = 0
        self.history = []

        system = f"""Ты {interviewer_role}. Проводишь собеседование на позицию {self.vacancy}.

Кандидат: {self.candidate_name}
Образование: {specialty}
Навыки: {skills}
{exp_text}
Личные качества: {personal}

Тип собеседования: {type_desc.get(interview_type, type_desc["hr"])}

ПРАВИЛА:
1. Представься: "Здравствуйте, я {interviewer_role}"
2. НЕ используй "меня зовут" и НЕ вставляй [Ваше имя]
3. Задавай ТОЛЬКО ОДИН вопрос за раз
4. Вопросы должны быть по теме {self.vacancy}
5. Используй данные кандидата (навыки, опыт)

ПРИМЕР ПРАВИЛЬНОГО НАЧАЛА:
"Здравствуйте, я {interviewer_role}. Какой у вас опыт в {self.vacancy}?"

Начни собеседование. Представься и задай первый вопрос."""

        return self._send(system, "start")

    def _get_interviewer_role(self, vacancy: str, interview_type: str) -> str:
        """Определяет должность интервьюера в зависимости от вакансии"""
        vacancy_lower = vacancy.lower()

        # Медицина
        if any(word in vacancy_lower for word in ['фельдшер', 'врач', 'медсестра', 'хирург', 'терапевт', 'скорая']):
            if interview_type == "hr":
                return "HR-специалист медицинского центра"
            elif interview_type == "technical":
                return "Заведующий отделением"
            else:
                return "Старший фельдшер"

        # Металлургия
        if any(word in vacancy_lower for word in ['металлург', 'сталевар', 'прокатчик', 'литейщик', 'завод']):
            if interview_type == "hr":
                return "HR-специалист завода"
            elif interview_type == "technical":
                return "Начальник цеха"
            else:
                return "Мастер участка"

        # IT / Программирование
        if any(word in vacancy_lower for word in
               ['программист', 'разработчик', 'python', 'java', 'фронтенд', 'бэкенд', 'it']):
            if interview_type == "hr":
                return "IT-рекрутер"
            elif interview_type == "technical":
                return "Tech Lead"
            else:
                return "Team Lead"

        # Строительство
        if any(word in vacancy_lower for word in ['строитель', 'прораб', 'инженер-строитель', 'стройка']):
            if interview_type == "hr":
                return "HR-специалист строительной компании"
            elif interview_type == "technical":
                return "Главный инженер"
            else:
                return "Руководитель проекта"

        # По умолчанию
        if interview_type == "hr":
            return "HR-менеджер"
        elif interview_type == "technical":
            return "Руководитель отдела"
        else:
            return "Ведущий специалист"

    def answer(self, user_answer: str) -> str:
        self.question_count += 1
        self.history.append({"role": "user", "content": user_answer})

        if self.question_count >= self.max_questions:
            prompt = f"""Собеседование окончено.
Выдай короткий отчёт по итогам собеседования на {self.vacancy}:
- Сильные стороны
- Что можно улучшить
- Рекомендация"""
        else:
            prompt = f"""Дай короткую обратную связь (1 предложение).
Затем задай следующий вопрос ({self.question_count + 1} из {self.max_questions}).
Вопрос должен быть по теме {self.vacancy}."""

        return self._send(None, prompt)

    def _send(self, system: str, prompt: str) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(self.history)
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.8,
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            result = response.json()
            reply = result['choices'][0]['message']['content']
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            logger.error(f"API Error: {e}")
            return "Ошибка. Попробуйте ещё раз."