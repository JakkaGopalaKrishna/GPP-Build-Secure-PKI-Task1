import os, base64, time
from datetime import datetime, timezone
import pyotp
DATA_PATH = "data/seed.txt"
OUT_PATH = "cron_out/last_code.txt"
def main():
    try:
        if not os.path.exists(DATA_PATH):
            return 1
        with open(DATA_PATH,"r") as f:
            seed_hex = f.read().strip()
        seed_bytes = bytes.fromhex(seed_hex)
        base32 = base64.b32encode(seed_bytes).decode().replace("=","")
        totp = pyotp.TOTP(base32, digits=6, interval=30)
        code = totp.now()
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH,"w") as f:
            f.write(f"{ts} - 2FA Code: {code}\n")
        return 0
    except Exception as e:
        print("ERROR:", e)
        return 2

if __name__ == "__main__":
    exit(main())