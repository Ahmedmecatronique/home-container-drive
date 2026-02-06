from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db

router = APIRouter(
    prefix="/container",
    tags=["container"],
)


@router.get("/health")
def container_health(db: Session = Depends(get_db)):
    """
    Endpoint de test pour la partie containers privés.
    """
    return {"status": "ok", "scope": "container"}

