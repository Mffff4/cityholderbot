import base64
import hashlib
import os
from datetime import datetime

def _generate_key():
    seed = int(datetime.now().strftime('%Y%m%d'))
    base = hashlib.sha256(str(seed).encode()).hexdigest()
    return int(base[:8], 16) % 1000000

def _load_secure_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 't.txt'), 'r') as f:
            return base64.b64decode(f.read().strip()).decode()
    except:
        return "0"

def _decode_ref(encoded_val: str) -> str:
    try:
        ref = _load_secure_data()
        if not ref or ref == "0":
            raise ValueError
        return ref
    except:
        return "0"

SECURE_CONSTANT = hashlib.sha256(b"cityholder_secure_key").hexdigest()[:16]
