import anthropic
from app.config import settings

SYSTEM_PROMPTS = {
    "ru": """Ты карьерный консультант КарИУ (Карагандинский индустриальный университет).
Помогаешь студентам и выпускникам с поиском работы, составлением резюме,
подготовкой к собеседованиям, поиском стажировок и переговорами о зарплате.
Отвечаешь на русском языке. Давай конкретные, практичные и применимые советы.""",

"kz": """Сен КарИУ (Қарағанды индустриялық университеті) мансап кеңесшісісің.
Студенттер мен түлектерге жұмыс іздеуге, түйіндеме жазуға,
сұхбатқа дайындалуға, тағылымдама табуға және жалақы туралы келіссөздерге көмектесесің.
Қазақ тілінде жауап бер. Нақты, практикалық және қолдануға болатын кеңестер бер.""",

"en": """You are a career consultant at KarIU (Karaganda Industrial University).
You help students and graduates with job searching, resume writing,
interview preparation, internship search, and salary negotiations.
Answer in English. Provide clear, practical, and actionable advice.""",
}


class AIChat:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def ask(self, message: str, graduate=None, lang: str = "ru") -> str:
        system = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["ru"])

        if graduate:
            system += f"\n\nКонтекст пользователя:\n{self._build_profile_context(graduate, lang)}"

        msg = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": message}],
        )
        return msg.content[0].text

    def _build_profile_context(self, graduate, lang: str) -> str:
        skills = ", ".join(s.name for s in graduate.skills) if graduate.skills else "—"
        if lang == "en":
            return (
                f"Major: {graduate.program.name if graduate.program else '—'}\n"
                f"Skills: {skills}\n"
                f"Work experience: {len(graduate.experiences)} entries"
            )
        return (
            f"Специальность: {graduate.program.name if graduate.program else '—'}\n"
            f"Навыки: {skills}\n"
            f"Опыт работы: {len(graduate.experiences)} записей"
        )