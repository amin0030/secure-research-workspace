import hashlib
from datetime import datetime, timezone


def format_utc(value: str) -> str:
    """Convert a timezone-aware timestamp to UTC."""
    if not isinstance(value, str):
        raise ValueError("Timestamp must be a string")

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError as error:
        raise ValueError("Invalid timestamp") from error

    if parsed.utcoffset() is None:
        raise ValueError("Timezone is required")

    if parsed.microsecond != 0:
        raise ValueError("Whole seconds are required")

    return parsed.astimezone(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def make_reference(booking_id: int, owner_user_id: str) -> str:
    """Create a stable confirmation reference, not an access token."""
    if type(booking_id) is not int or booking_id <= 0:
        raise ValueError("Invalid booking ID")

    if not isinstance(owner_user_id, str) or not owner_user_id.strip():
        raise ValueError("Invalid booking owner")

    source = f"{booking_id}:{owner_user_id}"

    return hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()[:12].upper()


def build_confirmation(booking: dict) -> dict:
    """Generate confirmation content for an active booking."""
    if booking.get("status") != "active":
        raise ValueError("Only active bookings can be confirmed")

    booking_id = booking["id"]
    room_id = booking["room_id"]
    owner = booking["owner_user_id"]

    if type(room_id) is not int or room_id <= 0:
        raise ValueError("Invalid room ID")

    reference = make_reference(booking_id, owner)
    starts_at = format_utc(booking["starts_at"])
    ends_at = format_utc(booking["ends_at"])

    if starts_at >= ends_at:
        raise ValueError("End time must be after start time")

    content = (
        f"Campus Room Booking Confirmation\n"
        f"Reference: {reference}\n"
        f"Booking ID: {booking_id}\n"
        f"Room ID: {room_id}\n"
        f"Student: {owner}\n"
        f"Start: {starts_at}\n"
        f"End: {ends_at}\n"
    )

    return {
        "reference": reference,
        "content": content,
    }
