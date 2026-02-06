from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import get_db
from . import models

router = APIRouter(
    prefix="/workspace",
    tags=["workspace"],
)

# Dossier du workspace sur le disque
WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "data" / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/health")
def health():
    return {"status": "ok", "area": "workspace"}


@router.get("/files")
def list_files(db: Session = Depends(get_db)):
    """
    Liste les fichiers connus dans la base pour le workspace.
    (plus tard on rajoutera les rôles / filtres)
    """
    files = (
        db.query(models.File)
        .filter(models.File.location_type == "workspace")
        .all()
    )
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "owner": f.owner,
            "path": f.path,
            "created_at": f.created_at,
        }
        for f in files
    ]


@router.post("/upload")
async def upload_file(
    username: str = Form(...),
    uploaded_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload d'un fichier dans le workspace.
    Pour l'instant, on passe 'username' à la main (on branchera avec le login plus tard).
    """

    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")

    # On construit un chemin simple : workspace/nom_du_fichier
    dest_path = WORKSPACE_DIR / uploaded_file.filename

    # Écriture du fichier sur le disque
    with dest_path.open("wb") as f:
        content = await uploaded_file.read()
        f.write(content)

    # Enregistrement en base
    db_file = models.File(
        filename=uploaded_file.filename,
        owner=username,
        path=str(dest_path),
        location_type="workspace",
        created_at=datetime.utcnow(),
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "message": "Fichier uploadé dans le workspace",
        "file": {
            "id": db_file.id,
            "filename": db_file.filename,
            "owner": db_file.owner,
            "path": db_file.path,
        },
    }


@router.get("/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    """
    Télécharge / ouvre un fichier du workspace à partir de son id.
    """
    db_file = (
        db.query(models.File)
        .filter(
            models.File.id == file_id,
            models.File.location_type == "workspace",
        )
        .first()
    )

    if not db_file:
        raise HTTPException(status_code=404, detail="Fichier introuvable en base")

    path = Path(db_file.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Fichier introuvable sur le disque")

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=db_file.filename,
    )
