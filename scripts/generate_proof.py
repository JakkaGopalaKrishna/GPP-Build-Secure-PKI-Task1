#python3
"""
Generate commit proof:
 - get latest commit hash (git)
 - sign ASCII commit hash with student private key (RSA-PSS-SHA256)
 - encrypt signature with instructor public key (RSA-OAEP-SHA256)
 - output commit hash and base64(encrypted_signature) as single-line string

Usage:
  python3 scripts/generate_proof.py
  python3 scripts/generate_proof.py --commit <40-char-hex>
  python3 scripts/generate_proof.py --priv keys/student_private.pem --instr keys/instructor_public.pem

Requirements:
  pip install cryptography
"""

import argparse
import subprocess
import base64
import sys
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ----------------------------
# Signing implementation
# ----------------------------
def sign_message(message: str, private_key) -> bytes:
    """
    Sign a message (ASCII string) using RSA-PSS with SHA-256 and max salt length.

    Args:
        message: ASCII/UTF-8 string to sign (commit hash)
        private_key: cryptography private key object

    Returns:
        signature bytes
    """
    if not isinstance(message, str):
        raise TypeError("message must be a string")
    msg_bytes = message.encode("utf-8")  # sign ASCII/UTF-8 string bytes

    signature = private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# ----------------------------
# Encryption implementation
# ----------------------------
def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA-OAEP with SHA-256 / MGF1(SHA256).

    Args:
        data: bytes to encrypt
        public_key: cryptography public key object

    Returns:
        ciphertext bytes
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# ----------------------------
# Helpers to load keys
# ----------------------------
def load_private_key(path: Path):
    b = path.read_bytes()
    return serialization.load_pem_private_key(b, password=None)

def load_public_key(path: Path):
    b = path.read_bytes()
    return serialization.load_pem_public_key(b)

# ----------------------------
# Get latest commit hash
# ----------------------------
def get_latest_commit_hash(repo_dir: Path) -> str:
    # Use `git` to get the commit hash
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%H"],
            capture_output=True,
            check=True,
            text=True,
        )
        commit = out.stdout.strip()
        if len(commit) != 40:
            raise ValueError(f"Unexpected commit hash length: '{commit}'")
        return commit
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Failed to get git commit hash. Are you in a git repo?") from e

# ----------------------------
# Main workflow
# ----------------------------
def main():
    p = argparse.ArgumentParser(description="Sign latest commit and encrypt signature")
    p.add_argument("--commit", help="40-char commit hash (optional)")
    p.add_argument("--priv", default="keys/student_private.pem", help="Path to student private PEM")
    p.add_argument("--instr", default="keys/instructor_public.pem", help="Path to instructor public PEM")
    p.add_argument("--repo", default=".", help="Repository root (default current dir)")
    args = p.parse_args()

    repo_dir = Path(args.repo).resolve()
    priv_path = Path(args.priv).resolve()
    instr_path = Path(args.instr).resolve()

    if not priv_path.exists():
        print(f"ERROR: private key not found at {priv_path}", file=sys.stderr)
        sys.exit(2)
    if not instr_path.exists():
        print(f"ERROR: instructor public key not found at {instr_path}", file=sys.stderr)
        sys.exit(2)

    # commit hash
    commit_hash = args.commit
    if not commit_hash:
        commit_hash = get_latest_commit_hash(repo_dir)

    if len(commit_hash) != 40:
        print("ERROR: commit hash must be 40 hex characters", file=sys.stderr)
        sys.exit(3)

    # load keys
    try:
        priv = load_private_key(priv_path)
    except Exception as e:
        print("ERROR: failed to load private key:", e, file=sys.stderr)
        sys.exit(4)
    try:
        instr_pub = load_public_key(instr_path)
    except Exception as e:
        print("ERROR: failed to load instructor public key:", e, file=sys.stderr)
        sys.exit(5)

    # sign commit hash
    try:
        signature = sign_message(commit_hash, priv)
    except Exception as e:
        print("ERROR: signing failed:", e, file=sys.stderr)
        sys.exit(6)

    # encrypt signature with instructor public key
    try:
        encrypted = encrypt_with_public_key(signature, instr_pub)
    except Exception as e:
        print("ERROR: encryption failed:", e, file=sys.stderr)
        sys.exit(7)

    # base64 encode (single line)
    enc_b64 = base64.b64encode(encrypted).decode("ascii")

    # Output results (plain)
    print("commit_hash:", commit_hash)
    print("encrypted_signature_base64:")
    print(enc_b64)

if __name__ == "__main__":
    main()
