import os
import shutil
from pathlib import Path
from typing import List, Optional
import aiofiles
from fastapi import UploadFile


class FileStorageService:
    """Service for managing file storage operations"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def list_files(self, path: str = "") -> List[dict]:
        """List all files and directories in the specified path"""
        target_path = self.storage_path / path
        
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
        target_dir = self.storage_path / path
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / file.filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {
            "filename": file.filename,
            "path": str(file_path.relative_to(self.storage_path)),
            "size": file_path.stat().st_size
        }
    
    def download_file(self, file_path: str) -> Optional[Path]:
        """Get the full path to a file for downloading"""
        full_path = self.storage_path / file_path
        
        if full_path.exists() and full_path.is_file():
            return full_path
        
        return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file or directory"""
        full_path = self.storage_path / file_path
        
        if not full_path.exists():
            return False
        
        if full_path.is_file():
            full_path.unlink()
        elif full_path.is_dir():
            shutil.rmtree(full_path)
        
        return True
    
    def create_directory(self, dir_path: str) -> dict:
        """Create a new directory"""
        full_path = self.storage_path / dir_path
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
