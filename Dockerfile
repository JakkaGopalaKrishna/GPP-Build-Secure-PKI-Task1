# ---------- BUILDER STAGE ----------
    FROM python:3.11-slim AS builder

    # Prevent Python from writing .pyc files and buffer stdout
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    WORKDIR /tmp/build
    
    # Copy dependency manifest first for layer caching
    COPY requirements.txt .
    
    # Install build dependencies required to compile wheels
    RUN apt-get update \
        && apt-get install -y --no-install-recommends build-essential gcc libffi-dev libssl-dev \
        && python -m pip install --upgrade pip setuptools wheel \
        && python -m pip install --prefix=/install -r requirements.txt \
        && rm -rf /var/lib/apt/lists/*
    
    # ---------- RUNTIME STAGE ----------
    FROM python:3.11-slim
    
    # Ensure container uses UTC timezone
    ENV TZ=UTC
    
    WORKDIR /app
    
    # Install minimal system deps: cron for scheduled jobs and ca-certificates
    RUN apt-get update \
        && apt-get install -y --no-install-recommends cron ca-certificates tzdata \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy installed Python packages from builder
    COPY --from=builder /install /usr/local
    
    # Copy app code and scripts
    COPY . /app
    
    # Create volume mount points and set permissions
    RUN mkdir -p /data /cron /app/keys \
        && chown -R root:root /app \
        && chmod 755 /app
    
    # Install cron schedule file and script
    # Expect cron/totp_cron and scripts/cron_job.py to exist in repo
    RUN if [ -f /app/cron/totp_cron ]; then \
          cp /app/cron/totp_cron /etc/cron.d/totp_cron && chmod 0644 /etc/cron.d/totp_cron && crontab /etc/cron.d/totp_cron; \
        fi
    
    # Move cron script to /cron and ensure executable
    RUN if [ -f /app/scripts/cron_job.py ]; then \
          mv /app/scripts/cron_job.py /cron/cron_job.py && chmod +x /cron/cron_job.py; \
        fi
    
    # Expose API port (documentation and mapping)
    EXPOSE 8080
    
    # Volumes for persistent data
    VOLUME ["/data", "/cron"]
    
    # Ensure entrypoint present and executable
    COPY entrypoint.sh /app/entrypoint.sh
    RUN chmod +x /app/entrypoint.sh
    
    ENTRYPOINT ["/app/entrypoint.sh"]
    