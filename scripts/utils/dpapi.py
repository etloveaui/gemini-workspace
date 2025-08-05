import win32crypt  # pywin32
from pathlib import Path

def encrypt_to_file(plaintext: bytes, path: str) -> None:
    blob = win32crypt.CryptProtectData(plaintext, None, None, None, None, 0)
    Path(path).write_bytes(blob)

def decrypt_from_file(path: str) -> bytes:
    blob = Path(path).read_bytes()
    _, data = win32crypt.CryptUnprotectData(blob, None, None, None, None, 0)
    return data
# NOTE: user-scope 기본. 동일 PC/동일 사용자에서만 복호 가능.
