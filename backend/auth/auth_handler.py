import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from setting import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from user.USER_MGR_CTRL import get_username_by_api_key


logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def _mask_token(token: str) -> str:
    if not token:
        return ""
    if len(token) <= 12:
        return "****"
    return f"{token[:6]}...{token[-4:]}"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    token_preview = _mask_token(token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning(
                "jwt_missing_subject",
                extra={"credential_type": "jwt", "token_preview": token_preview},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning(
            "jwt_expired",
            extra={"credential_type": "jwt", "token_preview": token_preview},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期，请重新登录"
        )
    except jwt.PyJWTError:
        logger.warning(
            "jwt_invalid",
            extra={"credential_type": "jwt", "token_preview": token_preview},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception:
        logger.exception(
            "jwt_verify_unexpected_error",
            extra={"credential_type": "jwt", "token_preview": token_preview},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据"
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    bearer_token = credentials.credentials if credentials else None
    api_key_from_header = request.headers.get("X-API-Key")
    raw_token = bearer_token or api_key_from_header
    client_ip = request.client.host if request.client else None

    if not raw_token:
        logger.warning(
            "auth_missing_credentials",
            extra={
                "path": request.url.path,
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "client_ip": client_ip,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    if raw_token.startswith("wlk_"):
        username = await get_username_by_api_key(raw_token, client_ip)
        if username:
            return username

    try:
        payload = verify_token(raw_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return username
    except HTTPException as jwt_error:
        username = await get_username_by_api_key(raw_token, client_ip)
        if username:
            logger.info(
                "auth_api_key_fallback_success",
                extra={
                    "username": username,
                    "credential_type": "api_key",
                    "path": request.url.path,
                    "client_ip": client_ip,
                },
            )
            return username

        logger.warning(
            "auth_failed",
            extra={
                "path": request.url.path,
                "status_code": jwt_error.status_code,
                "client_ip": client_ip,
                "credential_type": "jwt_or_api_key",
                "token_preview": _mask_token(raw_token),
            },
        )
        raise jwt_error
