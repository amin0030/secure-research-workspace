
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import DB_PATH, initialize_database


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
def list_rooms():
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rooms = connection.execute(
            """
            SELECT id, name, capacity
            FROM rooms
            WHERE is_active = ?
            ORDER BY id
            """,
            (1,),
        ).fetchall()

    return {
        "rooms": [dict(room) for room in rooms]
    }
