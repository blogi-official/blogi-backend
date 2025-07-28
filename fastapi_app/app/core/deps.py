from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_internal_secret(x_internal_secret: str = Header(...)):
    if x_internal_secret != settings.internal_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal secret"
        )
