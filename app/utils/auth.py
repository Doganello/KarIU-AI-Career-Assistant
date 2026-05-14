from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.models.user import User

# Этот нужен только для документации Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def create_access_token(user_id: int) -> str:
    """Создание JWT токена"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def set_auth_cookie(response: Response, token: str):
    """Установка httpOnly cookie с токеном"""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",  # Доступна для всего сайта
    )


def clear_auth_cookie(response: Response):
    """Очистка cookie с токеном"""
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )


def get_token_from_request(request: Request) -> Optional[str]:
    """Извлекает токен из куки или заголовка Authorization"""
    # Сначала пробуем взять из куки
    token = request.cookies.get("access_token")

    # Если нет в куках, пробуем из заголовка Authorization (для мобильных клиентов)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    return token


async def get_current_user(
        request: Request,
        db: Session = Depends(get_db),
        token: Optional[str] = Depends(oauth2_scheme),  # Для Swagger
) -> User:
    """
    Получение текущего пользователя из токена в куке или заголовке
    """
    # Получаем токен из запроса
    access_token = get_token_from_request(request)

    # Если токена нет в куке, пробуем из параметра (для Swagger)
    if not access_token and token:
        access_token = token

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не предоставлен токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Декодируем токен
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен"
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Невалидный токен: {str(e)}"
        )

    # Ищем пользователя в БД
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    return user


async def get_current_user_optional(
        request: Request,
        db: Session = Depends(get_db),
) -> Optional[User]:
    """Получение текущего пользователя без ошибки (опционально)"""
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None