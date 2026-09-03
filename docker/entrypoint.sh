#!/bin/sh
set -e

echo "========================================"
echo "  CoinHub — Container Startup"
echo "========================================"

mkdir -p /app/staticfiles /app/media
chmod -R 755 /app/staticfiles /app/media

echo "--> Waiting for PostgreSQL..."

MAX_RETRIES=5
COUNT=0

until python check_db.py; do
  COUNT=$((COUNT + 1))
  if [ $COUNT -ge $MAX_RETRIES ]; then
    echo "========================================"
    echo "--> CRITICAL ERROR: Database failed to connect after $MAX_RETRIES attempts."
    echo "========================================"
    exit 1
  fi
  echo "--> Connection failed. Retrying in 3 seconds ($COUNT/$MAX_RETRIES)..."
  sleep 3
done

echo "--> Database connection established. Proceeding with migrations..."

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
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

  