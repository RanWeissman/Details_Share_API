FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels


# ---------- Final (runtime) ----------
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m appuser

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY main.py app_logging.py requirements.txt README.md ./
COPY database ./database/
COPY models ./models/
COPY templates ./templates/
COPY docs ./docs/

RUN mkdir -p /scripts/database && chown -R appuser:appuser /scripts

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
