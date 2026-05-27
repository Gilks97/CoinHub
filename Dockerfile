FROM python:3.12-slim

# ── System deps ────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── App user (non-root) ────────────────────────────────────────────────────────
RUN useradd --create-home appuser
WORKDIR /app

# ── Python dependencies ────────────────────────────────────────────────────────
COPY backend/requirements/ /tmp/requirements/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements/production.txt

# ── Copy project ───────────────────────────────────────────────────────────────
COPY backend/ .

# ── Static files & Entrypoint ──────────────────────────────────────────────────
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Give appuser access to the code base files
RUN mkdir -p /app/staticfiles /app/media \
 && chown -R appuser:appuser /app/staticfiles /app/media
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]