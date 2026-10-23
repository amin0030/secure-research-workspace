
import os

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(auto_error=False)

TOKEN_ISSUER = "campus-app-api"
TOKEN_AUDIENCE = "booking-service"


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    secret = os.environ.get("SERVICE_TOKEN_SECRET")

    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=503,
            detail="Service authentication is not configured",
        )

    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            audience=TOKEN_AUDIENCE,
            issuer=TOKEN_ISSUER,
            options={
                "require": [
                    "sub",
                    "role",
                    "permissions",
                    "exp",
                    "iat",
                    "iss",
                    "aud",
                ]
            },
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    if (
        not isinstance(claims.get("sub"), str)
        or not claims["sub"].strip()
        or not isinstance(claims.get("permissions"), list)
        or not all(
            isinstance(item, str)
            for item in claims["permissions"]
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid token claims",
        )

    return claims


def require_student(permission: str):
    def check_access(claims=Depends(verify_token)):
        if claims.get("role") != "student":
            raise HTTPException(
                status_code=403,
                detail="Student role required",
            )

        if permission not in claims["permissions"]:
            raise HTTPException(
                status_code=403,
                detail="Permission denied",
            )

        return claims

    return check_access

def require_admin(permission: str):
    def check_access(claims=Depends(verify_token)):
        if claims.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Administrator role required",
            )

        if permission not in claims["permissions"]:
            raise HTTPException(
                status_code=403,
                detail="Permission denied",
            )

        return claims

    return check_access
