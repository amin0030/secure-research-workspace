
import importlib.util
import os
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient


SECRET = "test-confirmation-secret-at-least-32-characters"

service_path = (
    Path(__file__).resolve().parents[1]
    / "services"
    / "confirmation_service"
    / "main.py"
)

spec = importlib.util.spec_from_file_location(
    "confirmation_security_test",
    service_path,
)

service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)


class ConfirmationScopeTests(unittest.TestCase):
    def make_token(self, booking_id, username="amin"):
        now = datetime.now(timezone.utc)

        claims = {
            "sub": username,
            "role": "student",
            "permissions": ["confirmations:generate"],
            "booking_id": booking_id,
            "iss": "campus-app-api",
            "aud": "confirmation-service",
            "iat": int(now.timestamp()),
            "exp": int(
                (now + timedelta(minutes=1)).timestamp()
            ),
        }

        return jwt.encode(
            claims,
            SECRET,
            algorithm="HS256",
        )

    def test_wrong_booking_scope_rejected(self):
        booking = {
            "id": 1,
            "room_id": 2,
            "owner_user_id": "amin",
            "starts_at": "2027-07-20T10:00:00Z",
            "ends_at": "2027-07-20T11:00:00Z",
            "status": "active",
        }

        token = self.make_token(booking_id=2)

        with patch.dict(
            os.environ,
            {"CONFIRMATION_TOKEN_SECRET": SECRET},
        ):
            with TestClient(service.app) as client:
                response = client.post(
                    "/generate",
                    headers={
                        "Authorization": f"Bearer {token}"
                    },
                    json={"booking": booking},
                )

        self.assertEqual(
            response.status_code,
            403,
            response.text,
        )

    def test_wrong_booking_owner_rejected(self):
        booking = {
            "id": 1,
            "room_id": 2,
            "owner_user_id": "casper",
            "starts_at": "2027-07-20T10:00:00Z",
            "ends_at": "2027-07-20T11:00:00Z",
            "status": "active",
        }

        token = self.make_token(
            booking_id=1,
            username="amin",
        )

        with patch.dict(
            os.environ,
            {"CONFIRMATION_TOKEN_SECRET": SECRET},
        ):
            with TestClient(service.app) as client:
                response = client.post(
                    "/generate",
                    headers={
                        "Authorization": f"Bearer {token}"
                    },
                    json={"booking": booking},
                )

        self.assertEqual(
            response.status_code,
            403,
            response.text,
        )


if __name__ == "__main__":
    unittest.main()
