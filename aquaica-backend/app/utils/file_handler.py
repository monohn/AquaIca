import aiofiles
import os
import uuid
from pathlib import Path
from fastapi import UploadFile

# Assuming settings or base path is defined somewhere, falling back to local directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "media")

async def save_upload_file(file: UploadFile, subdirectory: str) -> tuple[str, str, str]:
    """Save uploaded file and return (file_path, file_name, file_type)."""
    target_dir = Path(UPLOAD_DIR) / subdirectory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = target_dir / unique_name
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    return str(file_path), file.filename, file.content_type

def delete_file(file_path: str) -> bool:
    """Delete a file from disk."""
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
            return True
    except Exception:
        pass
    return False
