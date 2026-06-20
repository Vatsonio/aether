# Aether — Multi-stage Dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final image
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy app
COPY backend backend/
COPY static static/
COPY config config/

EXPOSE 8090

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8090"]
