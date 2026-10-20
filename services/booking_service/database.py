
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


def get_connection(db_path=None):
    path = Path(db_path) if db_path is not None else DB_PATH

    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path=None):
    path = Path(db_path) if db_path is not None else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection(path)

    try:
        with connection:

            # Study rooms
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    capacity INTEGER NOT NULL
                        CHECK (capacity > 0),
                    is_active INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1))
                )
                """
            )

            connection.executemany(
                """
                INSERT OR IGNORE INTO rooms
                    (id, name, capacity)
                VALUES (?, ?, ?)
                """,
                SEED_ROOMS,
            )

            # Student bookings
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER NOT NULL,
                    owner_user_id TEXT NOT NULL
                        CHECK (length(trim(owner_user_id)) > 0),
                    starts_at TEXT NOT NULL,
                    ends_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'cancelled')),
                    created_at TEXT NOT NULL DEFAULT
                        (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

                    FOREIGN KEY (room_id)
                        REFERENCES rooms(id),

                    CHECK (starts_at < ends_at)
                )
                """
            )

            # Generated booking confirmations
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS confirmations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id INTEGER NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    generated_at TEXT NOT NULL DEFAULT
                        (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

                    FOREIGN KEY (booking_id)
                        REFERENCES bookings(id)
                )
                """
            )

            # Security audit events
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor_user_id TEXT,
                    action TEXT NOT NULL,
                    booking_id INTEGER,
                    occurred_at TEXT NOT NULL DEFAULT
                        (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

                    FOREIGN KEY (booking_id)
                        REFERENCES bookings(id)
                )
                """
            )

            # Database indexes
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_bookings_owner
                ON bookings(owner_user_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_bookings_room_times
                ON bookings(room_id, starts_at, ends_at)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_audit_events_time
                ON audit_events(occurred_at)
                """
            )

            # Prevent overlapping active bookings
            connection.execute(
                """
                CREATE TRIGGER IF NOT EXISTS
                    prevent_overlapping_bookings_insert
                BEFORE INSERT ON bookings
                WHEN NEW.status = 'active'
                BEGIN
                    SELECT RAISE(ABORT, 'overlapping booking')
                    WHERE EXISTS (
                        SELECT 1
                        FROM bookings
                        WHERE room_id = NEW.room_id
                          AND status = 'active'
                          AND NEW.starts_at < ends_at
                          AND NEW.ends_at > starts_at
                    );
                END
                """
            )

            connection.execute(
                """
                CREATE TRIGGER IF NOT EXISTS
                    prevent_overlapping_bookings_update
                BEFORE UPDATE OF
                    room_id, starts_at, ends_at, status
                ON bookings
                WHEN NEW.status = 'active'
                BEGIN
                    SELECT RAISE(ABORT, 'overlapping booking')
                    WHERE EXISTS (
                        SELECT 1
                        FROM bookings
                        WHERE id != NEW.id
                          AND room_id = NEW.room_id
                          AND status = 'active'
                          AND NEW.starts_at < ends_at
                          AND NEW.ends_at > starts_at
                    );
                END
                """
            )

        # Restrict database file access on Linux/Docker
        if os.name == "posix":
            os.chmod(path, 0o600)

    finally:
        connection.close()
