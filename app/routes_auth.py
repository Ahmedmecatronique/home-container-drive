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


# ----------------------------
# User / Settings endpoints
# ----------------------------
import json
from app.schemas import ChangePasswordRequest, SettingsUpdateRequest, BlockUserRequest, SettingsOut


@router.get("/me")
def me(username: str = None, db: Session = Depends(get_db)):
    """Return basic info about a user (for the frontend)."""
    if not username:
        raise HTTPException(status_code=400, detail="username required")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"username": user.username, "role": user.role}


@router.get("/settings/{username}", response_model=SettingsOut)
def get_settings(username: str, db: Session = Depends(get_db)):
    """Return user settings stored as JSON string."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    try:
        settings = json.loads(getattr(user, 'settings', None) or "{}")
    except Exception:
        settings = {}
    return {"username": user.username, "settings": settings}


@router.post("/settings/update")
def update_settings(payload: SettingsUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    # Merge existing settings with incoming
    try:
        existing = json.loads(getattr(user, 'settings', None) or "{}")
    except Exception:
        existing = {}
    existing.update(payload.settings or {})
    user.settings = json.dumps(existing)
    db.add(user)
    db.commit()
    return {"status": "ok", "settings": existing}


@router.post("/change_password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    # verify old password
    if not verify_password(payload.old_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Mot de passe invalide")
    # set new
    user.password_hash = hash_password(payload.new_password)
    db.add(user)
    db.commit()
    return {"status": "ok", "message": "Mot de passe modifié."}


@router.post("/block_user")
def block_user(payload: BlockUserRequest, db: Session = Depends(get_db)):
    """Block or unblock a target user by adding/removing them from settings.blocked (list)."""
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    try:
        s = json.loads(getattr(user, 'settings', None) or "{}")
    except Exception:
        s = {}
    blocked = set(s.get("blocked", []))
    if payload.action == "block":
        blocked.add(payload.target)
    else:
        blocked.discard(payload.target)
    s["blocked"] = list(blocked)
    user.settings = json.dumps(s)
    db.add(user)
    db.commit()
    return {"status": "ok", "blocked": s["blocked"]}
