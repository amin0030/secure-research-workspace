from urllib.parse import quote
from fastapi import Query
import os
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime as DateTime


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


class BookingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_id: int = Field(gt=0)
    starts_at: DateTime
    ends_at: DateTime


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    secret = os.environ.get("APP_TOKEN_SECRET")

    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured",
        )

    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            issuer="campus-app-api",
            audience="app-api",
            options={
                "require": [
                    "sub",
                    "role",
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
        claims.get("sub") not in {"amin", "casper", "frank", "rasmus"}
        or claims.get("role") not in {"student", "admin"}
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid token claims",
        )

    return claims


def student_user(claims=Depends(current_user)):
    if claims["role"] != "student":
        raise HTTPException(
            status_code=403,
            detail="Student role required",
        )

    return claims


def call_booking_service(
    method: str,
    path: str,
    claims: dict,
    permission: str,
    payload: dict | None = None,
):
    secret = os.environ.get("SERVICE_TOKEN_SECRET")
    service_url = os.environ.get("BOOKING_SERVICE_URL")

    if not secret or len(secret) < 32 or not service_url:
        raise HTTPException(
            status_code=503,
            detail="Booking integration is not configured",
        )

    now = datetime.now(timezone.utc)

    service_token = jwt.encode(
        {
            "sub": claims["sub"],
            "role": claims["role"],
            "permissions": [permission],
            "iss": "campus-app-api",
            "aud": "booking-service",
            "iat": now,
            "exp": now + timedelta(seconds=60),
        },
        secret,
        algorithm="HS256",
    )

    try:
        with httpx.Client(
            base_url=service_url,
            timeout=5.0,
            trust_env=False,
        ) as client:
            response = client.request(
                method,
                path,
                headers={
                    "Authorization": f"Bearer {service_token}"
                },
                json=payload,
            )
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail="Booking Service is unavailable",
        ) from error

    if response.status_code >= 500:
        raise HTTPException(
            status_code=502,
            detail="Booking Service returned an error",
        )

    try:
        result = response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail="Invalid Booking Service response",
        ) from error

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=result.get("detail", "Booking request rejected"),
        )

    return result


@router.get("/rooms")
def list_rooms(claims=Depends(current_user)):
    return call_booking_service(
        "GET", "/rooms", claims, "rooms:read"
    )


@router.post("/bookings", status_code=201)
def create_booking(
    booking: BookingInput,
    claims=Depends(student_user),
):
    return call_booking_service(
        "POST",
        "/bookings",
        claims,
        "bookings:create",
        booking.model_dump(mode="json"),
    )


@router.get("/bookings")
def list_bookings(claims=Depends(student_user)):
    return call_booking_service(
        "GET", "/bookings", claims, "bookings:read"
    )


@router.get("/bookings/{booking_id}")
def get_booking(
    booking_id: int = Path(gt=0),
    claims=Depends(student_user),
):
    return call_booking_service(
        "GET",
        f"/bookings/{booking_id}",
        claims,
        "bookings:read",
    )


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int = Path(gt=0),
    claims=Depends(student_user),
):
    return call_booking_service(
        "POST",
        f"/bookings/{booking_id}/cancel",
        claims,
        "bookings:cancel",
    )

@router.get("/rooms/search")
def search_rooms(
    q: str = Query(min_length=1, max_length=100),
    claims=Depends(current_user),
):
    return call_booking_service(
        "GET",
        f"/rooms/search?q={quote(q, safe='')}",
        claims,
        "rooms:read",
    )
