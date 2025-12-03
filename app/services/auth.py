from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User, RefreshToken, VerificationToken
from app.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.schemas.auth import UserCreate, LoginRequest
from app.config.settings import settings
from app.mailer.auth_mailer import AuthMailer

import secrets


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        token = self.create_verification_token(self.db, user.id)
        AuthMailer().send_verification_email(user.email, user.first_name, token)

        return user

    def authenticate_user(self, login_data: LoginRequest) -> Tuple[User, str, str]:
        user = self.db.query(User).filter(User.email == login_data.email).first()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Create tokens
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})

        # Store refresh token
        self._store_refresh_token(user.id, refresh_token)

        return user, access_token, refresh_token

    def _store_refresh_token(self, user_id: int, token: str):
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )

        self.db.add(refresh_token)
        self.db.commit()

    def generate_verification_token(self) -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)

    def create_verification_token(self, db: Session, user_id: int, expires_hours: int = 24):
        # Remove any existing tokens for this user
        db.query(VerificationToken).filter(
            VerificationToken.user_id == user_id
        ).delete()

        # Generate new token
        token = self.generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)

        # Store token
        verification_token = VerificationToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )

        db.add(verification_token)
        db.commit()

        return token

    def verify_token(self, db: Session, token: str):
        """Verify token and activate user"""

        # Find token
        verification_token = db.query(VerificationToken).filter(
            VerificationToken.token == token
        ).first()

        if not verification_token:
            return {"success": False, "message": "Invalid token"}

        # Check if token is expired
        if verification_token.expires_at < datetime.utcnow():
            # Delete expired token
            db.delete(verification_token)
            db.commit()
            return {"success": False, "message": "Token expired"}

        # Get user and mark as verified
        user = db.query(User).filter(User.id == verification_token.user_id).first()
        if user:
            user.is_verified = True
            user.is_active = True

            # Delete used token
            db.delete(verification_token)
            db.commit()

            return {"success": True, "message": "Email verified successfully"}

        return {"success": False, "message": "User not found"}

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if token exists in database and is not revoked
        token_record = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or expired"
            )

        # Get user
        user = self.db.query(User).filter(User.id == token_record.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        new_access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        new_refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})

        # Revoke old refresh token and store new one
        token_record.is_revoked = True
        self._store_refresh_token(user.id, new_refresh_token)
        self.db.commit()

        return new_access_token, new_refresh_token

    def logout(self, refresh_token: str):
        # Revoke the refresh token
        token_record = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()

        if token_record:
            token_record.is_revoked = True
            self.db.commit()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()