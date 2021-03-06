from Crypto.Cipher import AES
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from classifood import settings

import base64

def encrypt(s, secret_key=settings.AES_SECRET_KEY):
    if isinstance(s, basestring):
        # Pad string with NULL character until length is multiple of block_size
        s += ("\0" * (AES.block_size - (len(s) % AES.block_size)))
        aes = AES.new(secret_key)
        return base64.b32encode(aes.encrypt(s))
    return s

def decrypt(s, secret_key=settings.AES_SECRET_KEY):
    if isinstance(s, basestring):
        aes = AES.new(secret_key)
        return aes.decrypt(base64.b32decode(s)).rstrip("\0")
    return s

def get_hmac_sha256_hash(s, secret_key=settings.SECRET_KEY):
    if isinstance(s, basestring):
        return HMAC.new(secret_key, msg=s, digestmod=SHA256).hexdigest()
    return s
