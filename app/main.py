from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from . import models
from .routes_workspace import router as workspace_router
from .routes_container import router as container_router
from .routes_admin import router as admin_router
from .routes_auth import router as auth_router


def init_db():
    models
    Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    app = FastAPI(title="HOME CONTAINER DRIVE")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok", "project": "HOME_CONTAINER_DRIVE"}

    # enregistre nos routes API
    app.include_router(auth_router)
    app.include_router(workspace_router)
    app.include_router(container_router)
    app.include_router(admin_router)

    # Serveur du frontend
    static_dir = Path(__file__).resolve().parent.parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    def frontend():
        index_file = static_dir / "index.html"
        return index_file.read_text(encoding="utf-8")

    return app


init_db()
app = create_app()
