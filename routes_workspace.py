from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db

router = APIRouter(
    prefix="/workspace",
    tags=["workspace"],
)


@router.get("/health")
def workspace_health(db: Session = Depends(get_db)):
    """
    Endpoint de test pour le workspace.
    Vérifie qu'on peut accéder à la DB sans erreur.
    """
    return {"status": "ok", "scope": "workspace"}

