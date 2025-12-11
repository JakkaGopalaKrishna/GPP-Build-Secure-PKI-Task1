import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def generate_rsa_keypair(private_path="keys/student_private.pem", public_path="keys/student_public.pem"):
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    os.makedirs(os.path.dirname(private_path), exist_ok=True)
    with open(private_path, "wb") as f:
        f.write(priv_pem)
    with open(public_path, "wb") as f:
        f.write(pub_pem)
    os.chmod(private_path, 0o600)
    return private_path, public_path

def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def rsa_oaep_decrypt(private_key, ciphertext_bytes):
    return private_key.decrypt(
        ciphertext_bytes,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )

def rsa_pss_sign(private_key, message_bytes):
    return private_key.sign(
        message_bytes,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

def rsa_oaep_encrypt_with_pub(pub_key, data_bytes):
    return pub_key.encrypt(
        data_bytes,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )