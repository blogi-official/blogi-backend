from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

security = HTTPBearer(auto_error=True)


def decode_and_verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.django_secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")


def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    payload = decode_and_verify_token(token)

    if "user_id" not in payload:
        raise HTTPException(status_code=401, detail="user_id 정보가 없는 토큰입니다.")

    return {"token": token, "payload": payload}
