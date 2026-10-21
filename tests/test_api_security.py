
import json
import secrets
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:18000"


def api_request(method, path, token=None, payload=None):
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif method == "POST":
        data = b""

    request = Request(
        BASE_URL + path,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


class SecurityWorkflowTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        env_file = Path(__file__).resolve().parents[1] / ".env.local"

        values = dict(
            line.split("=", 1)
            for line in env_file.read_text(encoding="utf-8").splitlines()
            if "=" in line and not line.startswith("#")
        )

        cls.tokens = {}

        for username in ("amin", "casper", "rasmus"):
            status, result = api_request(
                "POST",
                "/login",
                payload={
                    "username": username,
                    "password": values[
                        f"CAMPUS_PASSWORD_{username.upper()}"
                    ],
                },
            )

            if status != 200:
                raise AssertionError(
                    f"Login setup failed for {username}: HTTP {status}"
                )

            cls.tokens[username] = result["access_token"]

    def create_test_booking(self):
        start = (
            datetime.now(timezone.utc)
            + timedelta(
                days=90,
                seconds=secrets.randbelow(30 * 86400),
            )
        ).replace(microsecond=0)

        end = start + timedelta(hours=1)

        payload = {
            "room_id": 3,
            "starts_at": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ends_at": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        status, result = api_request(
            "POST",
            "/bookings",
            self.tokens["amin"],
            payload,
        )

        self.assertEqual(status, 201)

        booking_id = result["booking"]["id"]

        self.addCleanup(
            api_request,
            "POST",
            f"/bookings/{booking_id}/cancel",
            self.tokens["amin"],
        )

        return booking_id, payload

    def test_01_missing_token_rejected(self):
        status, _ = api_request("GET", "/rooms")
        self.assertEqual(status, 401)

    def test_02_invalid_password_rejected(self):
        status, _ = api_request(
            "POST",
            "/login",
            payload={
                "username": "amin",
                "password": "intentionally-wrong-password",
            },
        )

        self.assertEqual(status, 401)

    def test_03_admin_cannot_create_student_booking(self):
        status, _ = api_request(
            "POST",
            "/bookings",
            self.tokens["rasmus"],
            {
                "room_id": 3,
                "starts_at": "2027-05-01T10:00:00Z",
                "ends_at": "2027-05-01T11:00:00Z",
            },
        )

        self.assertEqual(status, 403)

    def test_04_casper_cannot_access_amin_booking(self):
        booking_id, _ = self.create_test_booking()

        status, _ = api_request(
            "GET",
            f"/bookings/{booking_id}",
            self.tokens["casper"],
        )
        self.assertEqual(status, 404)

        status, _ = api_request(
            "POST",
            f"/bookings/{booking_id}/cancel",
            self.tokens["casper"],
        )
        self.assertEqual(status, 404)

    def test_05_invalid_booking_times_rejected(self):
        status, _ = api_request(
            "POST",
            "/bookings",
            self.tokens["amin"],
            {
                "room_id": 3,
                "starts_at": "2027-05-01T14:00:00Z",
                "ends_at": "2027-05-01T12:00:00Z",
            },
        )

        self.assertEqual(status, 422)

    def test_06_overlapping_bookings_rejected(self):
        _, payload = self.create_test_booking()

        status, _ = api_request(
            "POST",
            "/bookings",
            self.tokens["casper"],
            payload,
        )

        self.assertEqual(status, 409)

    def test_07_confirmation_workflow_and_ownership(self):
        booking_id, _ = self.create_test_booking()
        path = f"/bookings/{booking_id}/confirmation"

        status, generated = api_request(
            "POST",
            path,
            self.tokens["amin"],
        )

        self.assertEqual(status, 201)
        self.assertIn("Student: amin", generated["content"])

        status, saved = api_request(
            "GET",
            path,
            self.tokens["amin"],
        )

        self.assertEqual(status, 200)
        self.assertEqual(saved["content"], generated["content"])

        status, _ = api_request(
            "GET",
            path,
            self.tokens["casper"],
        )

        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
