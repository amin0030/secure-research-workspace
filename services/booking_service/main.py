
import sqlite3
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from auth import require_student, verify_token
from database import get_connection, initialize_database


class BookingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_id: int = Field(gt=0)
    starts_at: datetime
    ends_at: datetime


def to_utc_string(value: datetime) -> str:
    if value.utcoffset() is None:
        raise HTTPException(
            status_code=422,
            detail="Booking times must include a timezone",
        )

    utc_value = value.astimezone(timezone.utc)

    if utc_value.microsecond != 0:
        raise HTTPException(
            status_code=422,
            detail="Booking times must use whole seconds",
        )

    return utc_value.strftime("%Y-%m-%dT%H:%M:%SZ")


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Campus Room Booking - Booking Service",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "booking_service",
    }


@app.get("/rooms")
def list_rooms(claims=Depends(verify_token)):
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT id, name, capacity
            FROM rooms
            WHERE is_active = ?
            ORDER BY id
            """,
            (1,),
        ).fetchall()

    return {"rooms": [dict(row) for row in rows]}


@app.post("/bookings", status_code=201)
def create_booking(
    booking: BookingInput,
    claims=Depends(require_student("bookings:create")),
):
    starts_at = to_utc_string(booking.starts_at)
    ends_at = to_utc_string(booking.ends_at)

    if starts_at >= ends_at:
        raise HTTPException(
            status_code=422,
            detail="Start time must be before end time",
        )

    owner = claims["sub"]

    with closing(get_connection()) as connection:
        room = connection.execute(
            "SELECT id FROM rooms WHERE id = ? AND is_active = 1",
            (booking.room_id,),
        ).fetchone()

        if room is None:
            raise HTTPException(
                status_code=404,
                detail="Active room not found",
            )

        try:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO bookings
                        (room_id, owner_user_id, starts_at, ends_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (booking.room_id, owner, starts_at, ends_at),
                )

                booking_id = cursor.lastrowid

                connection.execute(
                    """
                    INSERT INTO audit_events
                        (actor_user_id, action, booking_id)
                    VALUES (?, ?, ?)
                    """,
                    (owner, "booking_created", booking_id),
                )

        except sqlite3.IntegrityError as error:
            if "overlapping booking" in str(error):
                raise HTTPException(
                    status_code=409,
                    detail="Room is already booked for this time",
                ) from error

            raise HTTPException(
                status_code=422,
                detail="Invalid booking data",
            ) from error

    return {
        "booking": {
            "id": booking_id,
            "room_id": booking.room_id,
            "owner_user_id": owner,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "status": "active",
        }
    }


@app.get("/bookings")
def list_bookings(
    claims=Depends(require_student("bookings:read")),
):
    with closing(get_connection()) as connection:
        rows = connection.execute(
            """
            SELECT id, room_id, owner_user_id,
                   starts_at, ends_at, status
            FROM bookings
            WHERE owner_user_id = ?
            ORDER BY starts_at
            """,
            (claims["sub"],),
        ).fetchall()

    return {"bookings": [dict(row) for row in rows]}


@app.get("/bookings/{booking_id}")
def get_booking(
    booking_id: int,
    claims=Depends(require_student("bookings:read")),
):
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT id, room_id, owner_user_id,
                   starts_at, ends_at, status
            FROM bookings
            WHERE id = ? AND owner_user_id = ?
            """,
            (booking_id, claims["sub"]),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    return {"booking": dict(row)}


@app.post("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    claims=Depends(require_student("bookings:cancel")),
):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                """
                UPDATE bookings
                SET status = 'cancelled'
                WHERE id = ?
                  AND owner_user_id = ?
                  AND status = 'active'
                """,
                (booking_id, claims["sub"]),
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Active booking not found",
                )

            connection.execute(
                """
                INSERT INTO audit_events
                    (actor_user_id, action, booking_id)
                VALUES (?, ?, ?)
                """,
                (claims["sub"], "booking_cancelled", booking_id),
            )

    return {
        "booking_id": booking_id,
        "status": "cancelled",
    }
