# ── CINEVERSE Backend Dockerfile ──────────────────────────────────────────
# Uses Python 3.11 slim for production stability (matching the model environment)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy download/verification helper script
COPY download_models.py .

# Copy application code
COPY app/ ./app/

# Copy model artifacts directory
COPY models/ ./models/

# Build-time verification & download:
# Checks whether models are actual binaries or Git LFS pointers.
# If pointer files are detected, automatically downloads actual binary assets
# and verifies similarity.pkl is ~176 MB (between 170 MB and 195 MB).
RUN python download_models.py models

# Expose backend port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:10000/')" || exit 1

# Start Uvicorn server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
