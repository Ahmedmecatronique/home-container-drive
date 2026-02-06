from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de la base SQLite (fichier home_container.db à la racine du projet)
SQLALCHEMY_DATABASE_URL = "sqlite:///./home_container.db"

# Engine = connexion à la base SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # nécessaire pour SQLite + threads
)

# Fabrique de sessions pour parler à la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de tous les modèles SQLAlchemy
Base = declarative_base()


# Dépendance FastAPI : fournit une session DB à chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

