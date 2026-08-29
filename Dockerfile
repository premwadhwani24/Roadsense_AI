# ==============================================================================
# RoadSense AI - Production Multi-Stage Dockerfile
# ==============================================================================

# --- Stage 1: Build & Dependency Resolution ---
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into wheels directory
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels gunicorn waitress


# --- Stage 2: Final Production Runtime ---
FROM python:3.11-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# Install runtime system libraries (OpenCV / GLib dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Create non-root system user for security hardening
RUN groupadd -r roadsense && useradd -r -g roadsense -d /app -s /sbin/nologin roadsense

# Copy application source code
COPY . /app

# Ensure directories for uploads, database, and logs exist with proper permissions
RUN mkdir -p /app/static/assets/uploads/videos \
             /app/static/assets/uploads/video_frames \
             /app/logs \
    && chown -R roadsense:roadsense /app

# Switch to non-root user
USER roadsense

EXPOSE 5000

# Docker Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production WSGI startup command using Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
