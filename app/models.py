from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "normal", "advanced", "admin"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings = Column(String, nullable=True, default="{}")  # JSON string with user preferences


class File(Base):
    """
    Fichiers du workspace OU des containers utilisateurs.
    location_type:
      - "workspace"
      - "container"
    """
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)      # chemin sur le disque (/data/...)
    owner = Column(String, nullable=False)     # username qui possède le fichier
    location_type = Column(String, nullable=False)  # "workspace" ou "container"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)

