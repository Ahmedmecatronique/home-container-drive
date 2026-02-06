from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os
from pathlib import Path

from config import settings
from storage_service import FileStorageService
from auth import verify_credentials

# Initialize FastAPI app
app = FastAPI(
    title="Mini-Cloud Storage",
    description="Local portable cloud storage system for Raspberry Pi",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage service
storage_service = FileStorageService(settings.storage_path)


@app.get("/")
async def root():
    """Serve the web interface"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        with open(html_path, "r") as f:
            return HTMLResponse(content=f.read())
    return {"message": "Mini-Cloud Storage API", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mini-cloud-storage"}


@app.get("/api/storage/info")
async def get_storage_info(username: str = Depends(verify_credentials)):
    """Get storage statistics"""
    return storage_service.get_storage_info()


@app.get("/api/files")
async def list_files(
    path: str = Query("", description="Path to list files from"),
    username: str = Depends(verify_credentials)
):
    """List all files and directories"""
    try:
        files = storage_service.list_files(path)
        return {"files": files, "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Query("", description="Path to upload file to"),
    username: str = Depends(verify_credentials)
):
    """Upload a file"""
    try:
        # Check file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_upload_size} bytes"
            )
        
        result = await storage_service.upload_file(file, path)
        return {"message": "File uploaded successfully", "file": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/download")
async def download_file(
    path: str = Query(..., description="Path to the file to download"),
    username: str = Depends(verify_credentials)
):
    """Download a file"""
    file_path = storage_service.download_file(path)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream"
    )


@app.delete("/api/files")
async def delete_file(
    path: str = Query(..., description="Path to the file or directory to delete"),
    username: str = Depends(verify_credentials)
):
    """Delete a file or directory"""
    try:
        success = storage_service.delete_file(path)
        
        if not success:
            raise HTTPException(status_code=404, detail="File or directory not found")
        
        return {"message": "File or directory deleted successfully", "path": path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/directories")
async def create_directory(
    path: str = Query(..., description="Path of the directory to create"),
    username: str = Depends(verify_credentials)
):
    """Create a new directory"""
    try:
        result = storage_service.create_directory(path)
        return {"message": "Directory created successfully", "directory": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
