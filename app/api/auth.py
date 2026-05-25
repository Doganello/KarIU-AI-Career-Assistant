from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.graduate import Graduate
from app.schemas.user import UserRegister, UserLogin, UserRead, TokenResponse
from app.utils.auth import create_access_token, set_auth_cookie, clear_auth_cookie, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(
        data: UserRegister,
        response: Response,
        db: Session = Depends(get_db)
):
    # Проверка длины пароля
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Пароль должен содержать минимум 6 символов")

    # Проверка существования пользователя
    if db.query(User).filter_by(email=data.email).first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    # Создание пользователя
    user = User(email=data.email)
    user.set_password(data.password)
    db.add(user)
    db.flush()

    # Создание профиля выпускника
    graduate = Graduate(user_id=user.id)
    db.add(graduate)
    db.commit()
    db.refresh(user)

    # Создание токена
    token = create_access_token(user.id)
    set_auth_cookie(response, token)

    return user


@router.post("/login", response_model=TokenResponse)
def login(
        data: UserLogin,
        response: Response,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(email=data.email).first()
    if not user or not user.check_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    token = create_access_token(user.id)
    set_auth_cookie(response, token)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user)):
    clear_auth_cookie(response)
    return {"message": "Успешный выход из системы"}


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/check")
def check_auth(current_user: User = Depends(get_current_user)):
    return {"authenticated": True, "user_id": current_user.id, "email": current_user.email}