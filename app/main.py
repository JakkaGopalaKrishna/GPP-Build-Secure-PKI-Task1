from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import base64, os, logging, time
from app.crypto_utils import load_private_key, load_public_key, rsa_oaep_decrypt, rsa_pss_sign, rsa_oaep_encrypt_with_pub
import pyotp
from datetime import datetime, timezone

DATA_PATH = "data/seed.txt"
LAST_CODE_PATH = "cron_out/last_code.txt"
STUDENT_PRIV = "keys/student_private.pem"
INSTRUCTOR_PUB = "keys/instructor_public.pem"

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

class CodeIn(BaseModel):
    code: str

@app.post("/decrypt-seed")
async def decrypt_seed(request: Request):
    try:
        body = await request.json()
        enc_b64 = body.get("encrypted_seed")
        if not enc_b64:
            raise HTTPException(status_code=400, detail={"error":"missing encrypted_seed"})
        try:
            ciphertext = base64.b64decode(enc_b64)
        except Exception:
            raise HTTPException(status_code=400, detail={"error":"invalid base64"})
        try:
            priv = load_private_key(STUDENT_PRIV)
        except Exception as e:
            logger.error("Failed to load private key: %s", e)
            raise HTTPException(status_code=500, detail={"error":"Private key unavailable"})
        try:
            plaintext = rsa_oaep_decrypt(priv, ciphertext)
            seed_hex = plaintext.decode()
            if len(seed_hex) != 64:
                logger.error("Seed length invalid: %s", seed_hex)
                raise HTTPException(status_code=500, detail={"error":"Decryption failed"})
            os.makedirs("/data", exist_ok=True)
            with open(DATA_PATH, "w") as f:
                f.write(seed_hex)
            os.chmod(DATA_PATH, 0o600)
            return {"status":"ok"}
        except Exception as e:
            logger.exception("Decryption failed")
            raise HTTPException(status_code=500, detail={"error":"Decryption failed"})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail={"error":"Internal server error"})

@app.get("/generate-2fa")
def generate_2fa():
    try:
        if not os.path.exists(DATA_PATH):
            raise HTTPException(status_code=500, detail={"error":"Seed unavailable"})
        with open(DATA_PATH,"r") as f:
            seed_hex = f.read().strip()
        seed_bytes = bytes.fromhex(seed_hex)
        base32 = base64.b32encode(seed_bytes).decode().replace("=", "")
        totp = pyotp.TOTP(base32, digits=6, interval=30)
        code = totp.now()
        now = int(time.time())
        elapsed = now % 30
        valid_for = 30 - elapsed
        return {"code": code, "valid_for": valid_for}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("generate-2fa error")
        raise HTTPException(status_code=500, detail={"error":"Internal server error"})

@app.post("/verify-2fa")
def verify_2fa(payload: CodeIn):
    code = payload.code
    if not code:
        raise HTTPException(status_code=400, detail={"error":"Missing code"})
    try:
        if not os.path.exists(DATA_PATH):
            raise HTTPException(status_code=500, detail={"error":"Seed unavailable"})
        with open(DATA_PATH,"r") as f:
            seed_hex = f.read().strip()
        seed_bytes = bytes.fromhex(seed_hex)
        base32 = base64.b32encode(seed_bytes).decode().replace("=", "")
        totp = pyotp.TOTP(base32, digits=6, interval=30)
        now = int(time.time())
        valid = False
        for shift in (-30,0,30):
            t = now + shift
            if totp.verify(code, for_time=t):
                valid = True
                break
        return {"valid": bool(valid)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("verify-2fa error")
        raise HTTPException(status_code=500, detail={"error":"Internal server error"})