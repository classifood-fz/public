from Crypto.Cipher import AES
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from classifood import settings

import base64

def encrypt(s, secret_key=settings.AES_SECRET_KEY):
    # Pad string with NULL character until length is multiple of block_size
    s += ("\0" * (AES.block_size - (len(s) % AES.block_size)))
    aes = AES.new(secret_key)
    return base64.b32encode(aes.encrypt(s))

def decrypt(s, secret_key=settings.AES_SECRET_KEY):
    aes = AES.new(secret_key)
    return aes.decrypt(base64.b32decode(s)).rstrip("\0")

def get_hmac_sha256_hash(s, secret_key):
    if isinstance(s, str) or isinstance(s, unicode):
        return HMAC.new(secret_key, msg=s, digestmod=SHA256).digest()
    else:
        return ''

def b64_encode(s):
    if isinstance(s, str) or isinstance(s, unicode):
        return base64.b64encode(s)
    else:
        return ''
