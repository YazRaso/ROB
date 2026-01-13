"""
This program is designed to encrypt variables of interest
"""

import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Initialize Fernet only if ENCRYPTION_KEY is set
if ENCRYPTION_KEY:
    fernet = Fernet(ENCRYPTION_KEY)
else:
    fernet = None
    print("Warning: ENCRYPTION_KEY not set. Encryption functions will not work.")


def encrypt_api_key(api_key: str) -> str:
    if fernet is None:
        raise ValueError("ENCRYPTION_KEY not configured. Please set it in .env file.")
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    if fernet is None:
        raise ValueError("ENCRYPTION_KEY not configured. Please set it in .env file.")
    return fernet.decrypt(encrypted_key.encode()).decode()
