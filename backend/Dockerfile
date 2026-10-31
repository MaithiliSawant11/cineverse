# ── CINEVERSE Backend Dockerfile ──────────────────────────────────────────
# Uses Python 3.11 slim for production stability (same as the pkl training env)
#
# Git LFS Note:
#   similarity.pkl (176 MB) is tracked by Git LFS.
#   When building this Docker image, Git must have already pulled the actual
#   file contents (not just the LFS pointer) BEFORE `docker build` runs.
#   On Render: enable "Docker LFS" in the service settings, or use the
#   `lfs: true` option in render.yaml (see render.yaml in repo root).
#
#   The pickle files are baked into the Docker image so Render doesn't need
#   any external storage at runtime. Docker image ~800 MB total.

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching — avoids reinstalling if code changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy model artifacts (pickle files)
# IMPORTANT: These must be the actual files, not Git LFS pointers.
# Verify: file size of similarity.pkl should be ~176 MB, not ~135 bytes.
COPY models/ ./models/

# Expose the port uvicorn will listen on
EXPOSE 8000

# Health check — wait up to 120s for model loading before reporting unhealthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Start the server
# --host 0.0.0.0 required for Render to receive traffic
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

