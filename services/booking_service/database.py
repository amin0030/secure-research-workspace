
import os
import sqlite3
from pathlib import Path


DB_PATH = Path(
    os.environ.get(
        "BOOKING_DB_PATH",
        str(Path(__file__).with_name("booking.sqlite3")),
    )
)

SEED_ROOMS = [
    (1, "Library Room A", 4),
    (2, "Library Room B", 6),
    (3, "Group Study Room C", 8),
]


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    capacity INTEGER NOT NULL CHECK (capacity > 0),
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1))
                )
                """
            )

            connection.executemany(
                """
                INSERT OR IGNORE INTO rooms (id, name, capacity)
                VALUES (?, ?, ?)
                """,
                SEED_ROOMS,
            )
    finally:
        connection.close()
