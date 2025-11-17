#!/bin/sh
set -e # Exit immediately if a command exits with a non-zero status.

# Entry point script: wait for DB readiness and run alembic migrations before starting the app.
# It then execs the CMD (uvicorn) as PID 1.

echo "Running migrations (alembic upgrade head)..."

# Load environment variables from .env if present so alembic and the app see them.
# Use `set -a` to export all variables defined in the file.
if [ -f "/app/.env" ]; then
  echo "Loading environment from /app/.env"
  set -a
  # shellcheck disable=SC1091
  . /app/.env
  set +a
fi

MAX_RETRIES=1
RETRY=0
while true; do
  if alembic upgrade head; then
    echo "Migrations applied successfully."
    break
  fi
  RETRY=$((RETRY + 1))
  if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
    echo "Failed to apply migrations after $RETRY attempts." >&2
    exit 1
  fi
  echo "Waiting for database to be ready... (attempt $RETRY/$MAX_RETRIES)" >&2
  sleep 2
done

# Start the main process
echo "Starting application..."
exec "$@"
