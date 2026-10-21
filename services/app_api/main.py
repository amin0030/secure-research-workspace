
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import jwt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field


app = FastAPI(title="Campus Room Booking - Application API")

SEED_USERS = {
    "amin": "student",
    "casper": "student",
    "frank": "student",
    "rasmus": "admin",
}

PASSWORD_ITERATIONS = 600_000
TOKEN_LIFETIME_MINUTES = 15


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )


@lru_cache(maxsize=1)
def load_users():
    users = {}

    for username, role in SEED_USERS.items():
        password = os.environ.get(
            f"CAMPUS_PASSWORD_{username.upper()}"
        )

        if not password or len(password) < 12:
            raise HTTPException(
                status_code=503,
                detail="Login is not configured",
            )

        salt = secrets.token_bytes(16)

        users[username] = {
            "role": role,
            "salt": salt,
            "password_hash": hash_password(password, salt),
        }

    return users


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "app_api",
    }


@app.post("/login")
def login(data: LoginInput):
    secret = os.environ.get("APP_TOKEN_SECRET")

    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=503,
            detail="Token signing is not configured",
        )

    users = load_users()
    username = data.username.strip().lower()
    user = users.get(username)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    submitted_hash = hash_password(
        data.password,
        user["salt"],
    )

    if not hmac.compare_digest(
        submitted_hash,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    now = datetime.now(timezone.utc)

    claims = {
        "sub": username,
        "role": user["role"],
        "iss": "campus-app-api",
        "aud": "app-api",
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_LIFETIME_MINUTES),
    }

    token = jwt.encode(
        claims,
        secret,
        algorithm="HS256",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900,
        "role": user["role"],
    }
from booking_proxy import router as booking_router

app.include_router(booking_router)

from confirmation_proxy import router as confirmation_router

app.include_router(confirmation_router)