
from fastapi import FastAPI

app = FastAPI(title="Campus Room Booking - Application API")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "app_api"
    }
