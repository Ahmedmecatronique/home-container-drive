from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from . import models

# PBKDF2 sécurisé
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------
# 🔵 AUTH UTILITIES
# ---------------------------------------------------------

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# ---------------------------------------------------------
# 🟦 FAKE TOKEN (pas de JWT → simple, stable, compatible frontend)
# ---------------------------------------------------------
def create_access_token(data: dict) -> str:
    """
    Au lieu d’un vrai JWT, on génère un simple token unique.
    Le frontend n’a pas besoin de JWT pour fonctionner.
    """
    token = f"TOKEN-{uuid.uuid4()}"
    return token
