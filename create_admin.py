from getpass import getpass

from app.database import SessionLocal, Base, engine
from app import models
from app.auth import hash_password


def init_db():
    """
    Crée les tables dans la base SQLite si elles n'existent pas encore.
    Utilisé ici car on n'importe pas app.main (pas de FastAPI lancé).
    """
    # on s'assure que les modèles sont importés
    models  # ne pas enlever
    Base.metadata.create_all(bind=engine)


def main():
    # s'assurer que les tables existent
    init_db()

    db = SessionLocal()

    print("=== Création d'un utilisateur ADMIN ===")
    username = input("Nom d'utilisateur admin : ").strip()

    # Vérifier si l'utilisateur existe déjà
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        print(f"[!] L'utilisateur '{username}' existe déjà avec le rôle '{existing.role}'.")
        db.close()
        return

    password = getpass("Mot de passe : ")
    password_confirm = getpass("Confirmer le mot de passe : ")

    if password != password_confirm:
        print("[!] Les mots de passe ne correspondent pas.")
        db.close()
        return

    # Créer l'utilisateur admin
    user = models.User(
        username=username,
        password_hash=hash_password(password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"[OK] Utilisateur admin créé avec l'id {user.id} et le username '{user.username}'.")
    db.close()


if __name__ == "__main__":
    main()

