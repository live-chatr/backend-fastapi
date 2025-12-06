from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from app.dependencies import get_db
from app.services.auth import AuthService
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
    RefreshTokenRequest
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    return user


@router.get("/verify-email")
async def verify_email_page(
        token: str,
        db: Session = Depends(get_db)
):
    print(f"reached here {token}")
    result = AuthService(db).verify_token(token)
    return result

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user, access_token, refresh_token = auth_service.authenticate_user(login_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    access_token, refresh_token = auth_service.refresh_access_token(request.refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/logout")
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    auth_service.logout(request.refresh_token)

    return {"message": "Successfully logged out"}