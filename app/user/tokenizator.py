import time
import uuid
from datetime import (
    timedelta,
    datetime
    )

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.x509 import load_pem_x509_certificate
from jwt import PyJWTError

from app import models
from app.config import settings
from app.user import schemas
from app.user.exceptions import (
    CREDENTIALS_EXCEPTION,
    INVALID_TOKEN_EXCEPTION
    )

from fastapi import (
    Request,
    HTTPException
    )
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
    )

JWKS_URI = f"https://login.microsoftonline.com/common/discovery/v2.0/keys"


def create_bearer_token(user_id: uuid.UUID) -> schemas.Token:
    expires_delta = datetime.utcnow() + timedelta(minutes=settings.jwt_exp)
    to_encode = {
        "exp": expires_delta,
        "sub": str(user_id)
        }
    token = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
        )
    return schemas.Token(access_token=token)


async def validate_token(token: str) -> schemas.User:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
            )
    except PyJWTError:
        raise CREDENTIALS_EXCEPTION

    user = await models.User.objects.get_or_none(id=uuid.UUID(payload["sub"]))
    if not user:
        raise CREDENTIALS_EXCEPTION
    return schemas.User.parse_obj(user)


async def decode_azure_id_token(token: str) -> dict:
    kid = jwt.get_unverified_header(token)["kid"]
    ms_pub_key = await get_public_key(kid)
    try:
        user_info = jwt.decode(
            token,
            ms_pub_key,
            algorithms=["RS256"],
            audience=settings.azure_client_id,
            options={
                "verify_signature": True
                }
            )
        return user_info
    except PyJWTError:
        raise INVALID_TOKEN_EXCEPTION


async def get_public_key(kid: str) -> RSAPublicKey:
    keys = requests.get(JWKS_URI, params={
        "appid": settings.azure_client_id
        }).json()["keys"]

    key_ = None
    for key in keys:
        if key["kid"] == kid:
            key_ = key['x5c'][0]

    pemstart = "-----BEGIN CERTIFICATE-----\n"
    pemend = "\n-----END CERTIFICATE-----\n"

    cert_str = pemstart + key_ + pemend
    cert_bytes = cert_str.encode(encoding="ascii")

    cert_obj = load_pem_x509_certificate(cert_bytes, default_backend())
    public_key = cert_obj.public_key()
    return public_key


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
            ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_token(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_token(token: str) -> bool:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
                )
        except PyJWTError:
            return False
        if payload.get('exp') >= time.time():
            return True
        return False
