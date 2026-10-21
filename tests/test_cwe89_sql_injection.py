
import unittest
from pathlib import Path

import httpx


BASE_URL = "http://127.0.0.1:18000"


def get_amin_password():
    env_file = Path(__file__).resolve().parents[1] / ".env.local"

    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("CAMPUS_PASSWORD_AMIN="):
            return line.split("=", 1)[1].strip()

    raise RuntimeError("CAMPUS_PASSWORD_AMIN not found")


class CWE89SQLInjectionTests(unittest.TestCase):
    def test_room_search_blocks_sql_injection(self):
        with httpx.Client(timeout=15.0) as client:
            login = client.post(
                f"{BASE_URL}/login",
                json={
                    "username": "amin",
                    "password": get_amin_password(),
                },
            )

            self.assertEqual(login.status_code, 200)

            headers = {
                "Authorization": (
                    f"Bearer {login.json()['access_token']}"
                )
            }

            rooms_response = client.get(
                f"{BASE_URL}/rooms",
                headers=headers,
            )

            self.assertEqual(rooms_response.status_code, 200)

            rooms = rooms_response.json()["rooms"]
            self.assertGreater(len(rooms), 0)

            room = rooms[0]

            valid = client.get(
                f"{BASE_URL}/rooms/search",
                headers=headers,
                params={"q": room["name"]},
            )

            self.assertEqual(valid.status_code, 200)
            self.assertIn(
                room["id"],
                [item["id"] for item in valid.json()["rooms"]],
            )

            attack = client.get(
                f"{BASE_URL}/rooms/search",
                headers=headers,
                params={
                    "q": "zzznoroom%' OR 1=1 -- "
                },
            )

            self.assertEqual(attack.status_code, 200)
            self.assertEqual(attack.json()["rooms"], [])


if __name__ == "__main__":
    unittest.main()