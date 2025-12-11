# GPP Task 1 - Build Secure PKI TOTP Microservice 
This repository implements the assignment:
- RSA 4096-bit keys
- RSA-OAEP (SHA-256) for seed decryption
- RSA-PSS (SHA-256, max salt) for signing
- TOTP (SHA-1, 30s, 6 digits)
- FastAPI endpoints: /decrypt-seed, /generate-2fa, /verify-2fa
- Docker multi-stage build, cron job, UTC timezone, volumes at /data and /cron_out