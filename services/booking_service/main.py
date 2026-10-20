
from fastapi import FastAPI

app = FastAPI(title="Campus Room Booking - Booking Service")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "booking_service"
    }
