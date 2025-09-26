from base64 import b64decode

from Crypto.Cipher import AES
from rpaatomic.types import Ciphertext


def decrypt(ciphertext: str, aes_key: str) -> str:
    key_bytes = aes_key.encode("utf-8")
    decoded = b64decode(ciphertext)
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    decrypted = cipher.decrypt(decoded)
    res = decrypted[: -decrypted[-1]] if decrypted else b""
    return res.decode("utf-8")


if __name__ == "__main__":
    a = Ciphertext("你好")
    print(a)
