from app.crypto_utils import generate_rsa_keypair

if __name__ == "__main__":
    priv, pub = generate_rsa_keypair()
    print("Generated keys/student_private.pem and keys/student_public.pem")