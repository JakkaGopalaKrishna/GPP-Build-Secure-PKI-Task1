# ---- builder ----
    FROM python:3.11-slim AS builder
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    WORKDIR /tmp/build
    COPY requirements.txt .
    RUN apt-get update && apt-get install -y build-essential gcc libffi-dev libssl-dev --no-install-recommends \
     && pip install --upgrade pip \
     && pip install --prefix=/install -r requirements.txt \
     && rm -rf /var/lib/apt/lists/*
    
    # ---- runtime ----
    FROM python:3.11-slim
    ENV TZ=UTC
    WORKDIR /app
    
    RUN apt-get update && apt-get install -y cron ca-certificates --no-install-recommends \
     && rm -rf /var/lib/apt/lists/*
    
    COPY --from=builder /install /usr/local
    COPY . /app
    
    RUN mkdir -p /data /cron_out /app/keys \
     && chmod 755 /app
    
    RUN cp /app/cron/totp_cron /etc/cron.d/totp_cron \
     && chmod 0644 /etc/cron.d/totp_cron \
     && crontab /etc/cron.d/totp_cron
    
    RUN mv /app/scripts/cron_job.py /cron/cron_job.py && chmod +x /cron/cron_job.py
    
    EXPOSE 8080
    VOLUME ["/data","/cron_out"]
    ENTRYPOINT ["/app/entrypoint.sh"]
    