import os
import shutil
from pathlib import Path
from typing import List, Optional
import aiofiles
from fastapi import UploadFile, HTTPException


class FileStorageService:
    """Service for managing file storage operations"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path).resolve()
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, path: str) -> Path:
        """Validate that the path is within storage directory and resolve it"""
        if not path:
            return self.storage_path
        
        # Remove any leading slashes and resolve the path
        clean_path = path.lstrip('/')
        full_path = (self.storage_path / clean_path).resolve()
        
        # Ensure the path is within storage directory
        try:
            full_path.relative_to(self.storage_path)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid path: Path traversal detected"
            )
        
        return full_path
    
    def list_files(self, path: str = "") -> List[dict]:
        """List all files and directories in the specified path"""
        target_path = self._validate_path(path)
        
        if not target_path.exists():
            return []
        
        items = []
        for item in target_path.iterdir():
            item_info = {
                "name": item.name,
                "path": str(item.relative_to(self.storage_path)),
                "is_directory": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": item.stat().st_mtime
            }
            items.append(item_info)
        
        return sorted(items, key=lambda x: (not x["is_directory"], x["name"]))
    
    async def upload_file(self, file: UploadFile, path: str = "") -> dict:
        """Upload a file to the specified path"""
        # Validate directory path
        target_dir = self._validate_path(path)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename - remove path separators and parent references
        safe_filename = Path(file.filename).name
        if not safe_filename or safe_filename in ['.', '..']:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = target_dir / safe_filename
        
        # Double-check the final path is still within storage
        try:
            file_path.resolve().relative_to(self.storage_path)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {
            "filename": safe_filename,
            "path": str(file_path.relative_to(self.storage_path)),
            "size": file_path.stat().st_size
        }
    
    def download_file(self, file_path: str) -> Optional[Path]:
        """Get the full path to a file for downloading"""
        full_path = self._validate_path(file_path)
        
        if full_path.exists() and full_path.is_file():
            return full_path
        
        return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file or directory"""
        full_path = self._validate_path(file_path)
        
        if not full_path.exists():
            return False
        
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(full_path)
        
        return True
    
    def create_directory(self, dir_path: str) -> dict:
        """Create a new directory"""
        full_path = self._validate_path(dir_path)
        full_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "name": full_path.name,
            "path": str(full_path.relative_to(self.storage_path))
        }
    
    def get_storage_info(self) -> dict:
        """Get storage statistics"""
        total_size = 0
        file_count = 0
        
        for item in self.storage_path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
        
        return {
            "total_size": total_size,
            "file_count": file_count,
            "storage_path": str(self.storage_path)
        }
