from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from config import settings

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify HTTP Basic authentication credentials"""
    
    correct_username = credentials.username == settings.api_username
    correct_password = credentials.password == settings.api_password
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username
