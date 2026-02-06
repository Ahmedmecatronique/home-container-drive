from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routes_workspace import router as workspace_router
from .routes_container import router as container_router
from .routes_admin import router as admin_router


def init_db():
    """
    Crée les tables dans la base SQLite si elles n'existent pas encore.
    """
    # Import des modèles pour que SQLAlchemy connaisse les tables
    models  # ne pas enlever : utilisé pour enregistrer les modèles
    Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    app = FastAPI(title="HOME CONTAINER DRIVE")

    # CORS minimal (on pourra durcir plus tard)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # plus tard: restreindre au LAN
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        """
        Endpoint global de test.
        """
        return {"status": "ok", "project": "HOME_CONTAINER_DRIVE"}

    # Enregistrer les sous-routers
    app.include_router(workspace_router)
    app.include_router(container_router)
    app.include_router(admin_router)

    return app


# Initialisation de la DB au chargement
init_db()

# Objet FastAPI utilisé par Uvicorn
app = create_app()

