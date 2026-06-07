from __future__ import annotations

from html import escape
from typing import Any


TELEGRAM_LIMIT = 3900


def chunks(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]
    result = []
    while text:
        part = text[:limit]
        cut = part.rfind("\n")
        if cut > 1000:
            part = part[:cut]
        result.append(part)
        text = text[len(part):].lstrip()
    return result


def vacancy_to_text(v: dict[str, Any]) -> str:
    salary = ""
    if v.get("salary_from") or v.get("salary_to"):
        salary = f"\n💰 Зарплата: {v.get('salary_from') or '—'}–{v.get('salary_to') or '—'}"

    city = f"\n📍 Город: {escape(str(v.get('city')))}" if v.get("city") else ""
    work_format = f"\n🏢 Формат: {escape(str(v.get('work_format')))}" if v.get("work_format") else ""
    source_url = f"\n🔗 Ссылка: {escape(str(v.get('source_url')))}" if v.get("source_url") else ""

    return (
        f"<b>{escape(str(v.get('title', 'Без названия')))}</b>\n"
        f"🏭 Компания: {escape(str(v.get('company') or 'не указана'))}"
        f"{city}{work_format}{salary}\n"
        f"🗂 Источник: {escape(str(v.get('source') or '—'))}"
        f"{source_url}\n"
        f"ID: <code>{v.get('id')}</code>"
    )


def profile_to_text(profile: dict[str, Any]) -> str:
    full_name = " ".join(
        str(profile.get(x) or "") for x in ["last_name", "first_name", "middle_name"]
    ).strip() or "не указано"
    return (
        "<b>👤 Твой профиль</b>\n\n"
        f"ФИО: {escape(full_name)}\n"
        f"Специальность: {escape(str(profile.get('specialty') or 'не указана'))}\n"
        f"Город: {escape(str(profile.get('city') or 'не указан'))}\n"
        f"Год выпуска: {escape(str(profile.get('grad_year') or 'не указан'))}\n"
        f"Заполненность: <b>{profile.get('profile_completeness', 0)}%</b>"
    )


def vacancy_full_text(v: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Название: {v.get('title') or ''}",
            f"Компания: {v.get('company') or ''}",
            f"Описание: {v.get('description') or ''}",
            f"Требования: {v.get('requirements') or ''}",
            f"Город: {v.get('city') or ''}",
            f"Формат: {v.get('work_format') or ''}",
            f"Отрасль: {v.get('industry') or ''}",
        ]
    )


def analysis_to_text(data: dict[str, Any]) -> str:
    if data.get("error"):
        return f"⚠️ {escape(str(data['error']))}"

    lines = ["<b>📄 Анализ вакансии</b>"]
    if "fit_score" in data:
        lines.append(f"\n✅ Совпадение: <b>{data.get('fit_score')}%</b>")
    if data.get("readiness_level"):
        lines.append(f"Готовность: <b>{escape(str(data.get('readiness_level')))}</b>")

    for title, key in [
        ("🧑‍💼 Вопросы на собеседовании", "key_questions"),
        ("📚 Что подготовить", "topics_to_prepare"),
        ("⚠️ Пробелы в компетенциях", "competence_gaps"),
    ]:
        items = data.get(key) or []
        if items:
            lines.append(f"\n<b>{title}</b>")
            lines.extend([f"- {escape(str(item))}" for item in items])
    return "\n".join(lines)
