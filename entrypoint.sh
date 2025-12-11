#!/usr/bin/env bash
set -e

# ensure directories
mkdir -p /data /cron_out /app/keys

# start cron (Debian): try service, fallback to cron
service cron start 2>/dev/null || (cron &)

# start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1