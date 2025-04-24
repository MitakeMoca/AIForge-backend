import secrets
import string

def generate_secret_key(length=32):
    alphabet = string.ascii_letters + string.digits
    secret_key = ''.join(secrets.choice(alphabet) for i in range(length))
    return secret_key