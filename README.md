# 🛡️ GPP – Build Secure PKI (Task 1)

A secure, containerized authentication microservice implementing:

- RSA-4096 public/private key cryptography  
- RSA-OAEP decryption  
- RSA-PSS signature generation  
- TOTP (Time-based One-Time Password) generation & verification  
- Docker multi-stage builds  
- Cron job for automatic TOTP logging  
- Persistent storage using Docker volumes  

This project follows enterprise-grade security practices and meets all requirements given in the GPP assignment.

---

## 📦 Features

### 🔐 Cryptographic Operations
- Generate RSA 4096-bit keys (PEM)
- Decrypt encrypted seed using **RSA-OAEP-SHA256**
- Sign commit hash using **RSA-PSS-SHA256**
- Encrypt signature using **RSA-OAEP-SHA256**
- Validate cryptographic inputs strictly

### 🔢 2FA – TOTP Implementation
- SHA-1 (default), 30-second window  
- 6-digit codes  
- Convert 64-character hex seed → Base32 → TOTP library  
- Verify codes with ±30 sec tolerance  

### 🐳 Dockerized API + Cron System
- Multi-stage Dockerfile  
- UTC timezone enforced  
- Cron logs TOTP code every minute → `/cron/last_code.txt`  
- Persistent volumes:  
  `/data` → decrypted seed  
  `/cron` → cron logs  

---

## 🗂️ Project Structure
```
GPP-Build-Secure-PKI
│
├── app/
│   ├── main.py                  # FastAPI / Flask API server
│   ├── crypto_utils.py          # RSA + TOTP cryptography functions
│   ├── totp_utils.py            # TOTP generation & verification
│   └── __init__.py
│
├── scripts/
│   ├── log_2fa_cron.py          # Cron-job TOTP generator
│   └── generate_proof.py        # Commit-proof generator
│
├── cron/
│   ├── 2fa-cron                 # Cron configuration (LF only)
│   └── last_code.txt            # Auto-generated TOTP logs
│
├── keys/
│   ├── student_private.pem
│   ├── student_public.pem
│   └── instructor_public.pem
│
├── data/
│   └── seed.txt                 # Decrypted seed (created after Step 4/5)
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md
```

# 🚀 How to Run the Project

## 1️⃣ Build & Run Docker

```
docker-compose build
docker-compose up -d
```

The API will start at:

```
http://localhost:8080
```

---

# 📡 API Endpoints

## **POST /decrypt-seed**
Decrypt the encrypted seed using RSA-OAEP-SHA256.

### Request:
```json
{
  "encrypted_seed": "BASE64_STRING"
}
```

### Success Response:
```json
{
  "status": "ok"
}
```

Seed is saved to:

```
/data/seed.txt
```

---

## **GET /generate-2fa**
Generate current TOTP code.

### Response:
```json
{
  "code": "123456",
  "valid_for": 18
}
```

---

## **POST /verify-2fa**
Verify a TOTP code with ±30 sec tolerance.

### Request:
```json
{
  "code": "123456"
}
```

### Response:
```json
{
  "valid": true
}
```

---

# ⏱️ Cron Job

The cron job runs every minute and logs:

```
YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX
```

Output file:

```
/cron/last_code.txt
```

Cron configuration (LF-ending required):

```
* * * * * cd /app && /usr/local/bin/python3 /scripts/log_2fa_cron.py >> /cron/last_code.txt 2>&1
```

---

# 🔒 Commit-Proof Generation (Step 13)

## 1️⃣ Get commit hash
```
git log -1 --format=%H
```

## 2️⃣ Generate encrypted commit proof
```
python3 scripts/generate_proof.py
```

### Output Example:
```
commit_hash: sdfgj...dfg
encrypted_signature_base64:
W89QF3Nd9YHhWVz2lP6e4....
```

Submit both values as required.

---

# 🧪 Testing Checklist

| Test | Expected |
|------|----------|
| `/decrypt-seed` | `{status:"ok"}` |
| `/generate-2fa` | 6-digit TOTP + valid_for |
| `/verify-2fa` | true/false |
| Restart container | Seed persists |
| Cron job | Logs every minute |
| Timezone | UTC |
| TOTP | Matches Google Authenticator |
