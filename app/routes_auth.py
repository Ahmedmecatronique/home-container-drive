from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from app import schemas

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):

    # Récupérer l'utilisateur
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
        )

    # Vérifier mot de passe
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
        )

    # Générer un vrai token JWT
    access_token = create_access_token(
        {"sub": user.username, "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
    }


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
@router.post("/register")
def register_user(payload: dict, db: Session = Depends(get_db)):
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Tous les champs sont obligatoires.")

    # Vérifier existence
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Nom d’utilisateur déjà utilisé.")

    # Créer nouvel utilisateur
    new_user = User(
        username=username,
        password_hash=hash_password(password),
        role="normal",
        created_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "ok",
        "message": "Compte créé avec succès.",
        "username": new_user.username
    }
