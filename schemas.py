from datetime import datetime
from pydantic import BaseModel


# ---------- Utilisateurs ----------

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


# ---------- Fichiers ----------

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


# ---------- Auth ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str

