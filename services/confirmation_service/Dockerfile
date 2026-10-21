
FROM python:3.12-slim

WORKDIR /app

COPY services/confirmation_service/requirements.txt ./requirements.txt

COPY packages/campus_confirmation /tmp/campus_confirmation

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir /tmp/campus_confirmation

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser

COPY services/confirmation_service/main.py .

USER appuser

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
