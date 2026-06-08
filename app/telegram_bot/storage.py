from dataclasses import dataclass
from typing import Optional


@dataclass
class UserSession:
    token: Optional[str] = None
    waiting_for: Optional[str] = None
    login_email: Optional[str] = None


_sessions: dict[int, UserSession] = {}


def get_session(telegram_user_id: int) -> UserSession:
    if telegram_user_id not in _sessions:
        _sessions[telegram_user_id] = UserSession()
    return _sessions[telegram_user_id]


def clear_session(telegram_user_id: int) -> None:
    _sessions.pop(telegram_user_id, None)