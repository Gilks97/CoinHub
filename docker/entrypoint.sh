#!/bin/sh
set -e

echo "========================================"
echo "  CoinHub — Container Startup"
echo "========================================"

# Ensure volume-mounted dirs are writable by appuser
mkdir -p /app/staticfiles /app/media

echo "--> Waiting for PostgreSQL to be ready..."
until python - <<'PYEOF'
import sys, os
try:
    import psycopg2
    psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
    ).close()
except Exception:
    sys.exit(1)
PYEOF
do
  echo "    PostgreSQL unavailable - retrying in 2s..."
  sleep 2
done
echo "--> PostgreSQL is ready."

echo "--> Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "--> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "--> Ensuring default superuser exists..."
python manage.py create_default_superuser

echo "--> Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --worker-class sync \
  --timeout 120 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
