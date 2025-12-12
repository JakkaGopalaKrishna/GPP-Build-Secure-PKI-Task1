#.env python3
# Cron script to log 2FA codes every minute
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from app.crypto_utils import generate_totp_code

SEED_PATH = "data/seed.txt"
OUTPUT_PATH = "cron/last_code.txt"


def read_seed() -> str:
    """Read 64-character hex seed."""
    if not os.path.exists(SEED_PATH):
        raise FileNotFoundError(f"Seed file not found at {SEED_PATH}")

    with open(SEED_PATH, "r") as f:
        seed = f.read().strip()

    if len(seed) != 64:
        raise ValueError("Seed must be 64 hex chars")

    return seed


def main():
    try:
        seed = read_seed()
        code = generate_totp_code(seed)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        output = f"{timestamp} - 2FA Code: {code}\n"

        with open(OUTPUT_PATH, "a") as f:
            f.write(output)

    except Exception as e:
        with open(OUTPUT_PATH, "a") as f:
            f.write(f"ERROR: {str(e)}\n")


if __name__ == "__main__":
    main()
