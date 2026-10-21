
import os
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Path

from booking_proxy import call_booking_service, student_user


router = APIRouter()


@router.post("/bookings/{booking_id}/confirmation", status_code=201)
def create_confirmation(
    booking_id: int = Path(gt=0),
    claims=Depends(student_user),
):
    # Step 1: Retrieve the booking with the student's identity.
    booking_response = call_booking_service(
        "GET",
        f"/bookings/{booking_id}",
        claims,
        "bookings:read",
    )

    booking = booking_response["booking"]

    if (
        booking["id"] != booking_id
        or booking["owner_user_id"] != claims["sub"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Booking ownership mismatch",
        )

    if booking["status"] != "active":
        raise HTTPException(
            status_code=409,
            detail="Only active bookings can be confirmed",
        )

    # Step 2: Create a short-lived, booking-scoped token.
    secret = os.environ.get("CONFIRMATION_TOKEN_SECRET")
    service_url = os.environ.get("CONFIRMATION_SERVICE_URL")

    if not secret or len(secret) < 32 or not service_url:
        raise HTTPException(
            status_code=503,
            detail="Confirmation integration is not configured",
        )

    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": claims["sub"],
            "role": "student",
            "permissions": ["confirmations:generate"],
            "booking_id": booking_id,
            "iss": "campus-app-api",
            "aud": "confirmation-service",
            "iat": now,
            "exp": now + timedelta(seconds=60),
        },
        secret,
        algorithm="HS256",
    )

    # Step 3: Generate the confirmation in the third service.
    try:
        with httpx.Client(
            base_url=service_url,
            timeout=5.0,
            trust_env=False,
        ) as client:
            response = client.post(
                "/generate",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json={"booking": booking},
            )
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail="Confirmation Service is unavailable",
        ) from error

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Confirmation generation failed",
        )

    try:
        generated = response.json()
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail="Invalid confirmation response",
        ) from error

    if (
        not isinstance(generated, dict)
        or generated.get("booking_id") != booking_id
        or not isinstance(generated.get("content"), str)
    ):
        raise HTTPException(
            status_code=502,
            detail="Invalid confirmation data",
        )

    # Step 4: Store it through Booking Service.
    # Confirmation Service never receives direct SQLite access.
    return call_booking_service(
        "POST",
        f"/bookings/{booking_id}/confirmation",
        claims,
        "confirmations:store",
        {"content": generated["content"]},
    )


@router.get("/bookings/{booking_id}/confirmation")
def read_confirmation(
    booking_id: int = Path(gt=0),
    claims=Depends(student_user),
):
    return call_booking_service(
        "GET",
        f"/bookings/{booking_id}/confirmation",
        claims,
        "confirmations:read",
    )
