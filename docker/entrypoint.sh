#!/bin/sh
set -e

echo "========================================"
echo "  CoinHub — Container Startup"
echo "========================================"

mkdir -p /app/staticfiles /app/media
chmod -R 755 /app/staticfiles /app/media

echo "--> Waiting for PostgreSQL..."

# Run database check using check_db.py
if ! python check_db.py; then
    echo "CRITICAL: Database check failed. Exiting container startup."
    exit 1
fi

echo "--> Database connection established. Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "--> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "--> Ensuring default superuser exists..."
python manage.py createsuperuser --noinput || true

echo "--> Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 3 \
  --worker-class sync \
  --timeout 120 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level info