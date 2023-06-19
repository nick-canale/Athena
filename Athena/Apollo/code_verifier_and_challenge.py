
import secrets
import base64
import hashlib


def sha256_hash(data):
    # Create a new SHA-256 hash object
    sha256_hash_object = hashlib.sha256()
    # Update the hash object with the data
    sha256_hash_object.update(data)
    # Get the hexadecimal representation of the hash digest
    hash_digest = sha256_hash_object.digest()
    return hash_digest

def get_code_verifier_and_challenge():
    secret = secrets.token_bytes(32)
    code_verifier = base64.b64encode(secret)
    code_challenge = base64.b64encode(sha256_hash(code_verifier))
    return code_verifier, code_challenge





























