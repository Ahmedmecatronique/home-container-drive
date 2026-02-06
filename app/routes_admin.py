from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/health")
def admin_health(db: Session = Depends(get_db)):
    """
    Endpoint de test pour la partie administration.
    """
    return {"status": "ok", "scope": "admin"}

