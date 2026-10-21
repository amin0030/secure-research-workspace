
import os
from typing import Literal

import jwt
from campus_confirmation import build_confirmation
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field


app = FastAPI(
    title="Campus Room Booking - Confirmation Service"
)

bearer_scheme = HTTPBearer(auto_error=False)


class BookingData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    owner_user_id: str = Field(min_length=1, max_length=100)
    starts_at: str
    ends_at: str
    status: Literal["active", "cancelled"]


class ConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking: BookingData


def verify_confirmation_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    secret = os.environ.get("CONFIRMATION_TOKEN_SECRET")

    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=503,
            detail="Confirmation authentication is not configured",
        )

    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            issuer="campus-app-api",
            audience="confirmation-service",
            options={
                "require": [
                    "sub",
                    "role",
                    "permissions",
                    "booking_id",
                    "iss",
                    "aud",
                    "iat",
                    "exp",
                ]
            },
        )
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        ) from error

    if (
        not isinstance(claims.get("sub"), str)
        or not claims["sub"].strip()
        or claims.get("role") != "student"
        or claims.get("permissions") != ["confirmations:generate"]
        or type(claims.get("booking_id")) is not int
        or claims["booking_id"] <= 0
    ):
        raise HTTPException(
            status_code=403,
            detail="Permission denied",
        )

    return claims


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "confirmation_service",
    }


@app.post("/generate")
def generate_confirmation(
    request: ConfirmationRequest,
    claims=Depends(verify_confirmation_token),
):
    booking = request.booking

    if (
        booking.id != claims["booking_id"]
        or booking.owner_user_id != claims["sub"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Booking does not match authorization",
        )

    try:
        result = build_confirmation(booking.model_dump())
    except (ValueError, KeyError, TypeError) as error:
        raise HTTPException(
            status_code=422,
            detail="Invalid booking for confirmation",
        ) from error

    return {
        "booking_id": booking.id,
        "reference": result["reference"],
        "content": result["content"],
    }
