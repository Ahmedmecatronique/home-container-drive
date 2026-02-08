from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# =======================
#   SCHÉMAS UTILISATEURS
# =======================

class UserBase(BaseModel):
    username: str
    role: str  # "normal", "advanced", "admin"


class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # "normal", "advanced", "admin"


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # pour convertir depuis un objet SQLAlchemy


# ====================
#   SCHÉMAS FICHIERS
# ====================

class FileBase(BaseModel):
    filename: str
    owner: str
    location_type: str  # "workspace" ou "container"


class FileOut(FileBase):
    id: int
    path: str
    created_at: datetime

    class Config:
        from_attributes = True


# ====================
#   SCHÉMAS AUTH
# ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Optional[str] = None
    username: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str


class SettingsUpdateRequest(BaseModel):
    username: str
    settings: dict


class BlockUserRequest(BaseModel):
    username: str
    target: str
    action: str  # "block" or "unblock"


class SettingsOut(BaseModel):
    username: str
    settings: dict

