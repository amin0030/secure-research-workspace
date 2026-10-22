
import os
import unittest
from pathlib import Path

import httpx


BASE_URL = os.environ.get(
    "CAMPUS_TEST_BASE_URL",
    "http://127.0.0.1:18000",
)


def get_amin_password():
    password = os.environ.get("CAMPUS_PASSWORD_AMIN")

    if password:
        return password

    env_file = Path(__file__).resolve().parents[1] / ".env.local"

    if not env_file.is_file():
        raise RuntimeError("CAMPUS_PASSWORD_AMIN is missing")

    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("CAMPUS_PASSWORD_AMIN="):
            return line.split("=", 1)[1].strip()

    raise RuntimeError("CAMPUS_PASSWORD_AMIN not found")


class CWE20TimezoneTests(unittest.TestCase):
    def test_end_before_start_with_different_timezones(self):
        with httpx.Client(timeout=15.0) as client:
            login = client.post(
                f"{BASE_URL}/login",
                json={
                    "username": "amin",
                    "password": get_amin_password(),
                },
            )

            self.assertEqual(login.status_code, 200)

            token = login.json()["access_token"]

            response = client.post(
                f"{BASE_URL}/bookings",
                headers={
                    "Authorization": f"Bearer {token}"
                },
                json={
                    "room_id": 2,
                    "starts_at": "2027-07-20T10:00:00+00:00",
                    "ends_at": "2027-07-20T11:00:00+02:00",
                },
            )

            self.assertEqual(
                response.status_code,
                422,
                response.text,
            )


if __name__ == "__main__":
    unittest.main()
