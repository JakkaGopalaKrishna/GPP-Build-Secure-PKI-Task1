#!.env bash
set -euo pipefail

# Make sure directories exist with correct perms
mkdir -p /data /cron /app/keys
chmod 755 /data /cron || true

# Start cron daemon (try service then fallback to cron in background)
if command -v service >/dev/null 2>&1; then
  service cron start || true
else
  cron || true
fi

# Give cron a second to start
sleep 1

# Start uvicorn (FastAPI app) — parents PID will be uvicorn
# --reload not used in production image
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 1