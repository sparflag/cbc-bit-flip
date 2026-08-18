#!/usr/bin/env python3
"""CBC Bit Flip — real mini-challenge (cbc-bit-flip)."""
import base64, hashlib, hmac, json, os, re, sqlite3, sys, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote, quote

sys.path.insert(0, "/challenge/_shared")
from fetch_material import fetch_material

CHALLENGE_KEY = os.environ.get("CHALLENGE_KEY", 'iv-manipulation')
_MAT = {}

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

TOKEN_KEY = hashlib.md5(b"cbc-bitflip").digest()
TOKEN_IV = hashlib.md5(b"iv-cbc-bitflip").digest()

def pkcs7_pad(data, block=16):
    pad = block - (len(data) % block)
    return data + bytes([pad] * pad)

def pkcs7_unpad(data):
    pad = data[-1]
    if pad < 1 or pad > 16 or data[-pad:] != bytes([pad] * pad):
        raise ValueError("bad padding")
    return data[:-pad]

def aes_cbc_encrypt(pt, iv=TOKEN_IV):
    cipher = Cipher(algorithms.AES(TOKEN_KEY), modes.CBC(iv), backend=default_backend())
    enc = cipher.encryptor()
    return enc.update(pkcs7_pad(pt)) + enc.finalize()

def aes_cbc_decrypt(ct, iv=TOKEN_IV):
    cipher = Cipher(algorithms.AES(TOKEN_KEY), modes.CBC(iv), backend=default_backend())
    dec = cipher.decryptor()
    return pkcs7_unpad(dec.update(ct) + dec.finalize())

def make_token():
    return base64.b64encode(TOKEN_IV + aes_cbc_encrypt(b"role=user")).decode()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/plain", headers=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        data = body if isinstance(body, bytes) else body.encode()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


    def do_GET(self):
        p = urlparse(self.path)
        qs = parse_qs(p.query)
        if p.path == "/flag":
            return self._send(200, _MAT.get("delivery_blob", "") + "\n")
        if p.path == "/token":
            return self._send(200, make_token() + "\n")
        if p.path == "/admin":
            tok = qs.get("token", [""])[0]
            try:
                raw = base64.b64decode(tok)
                iv, ct = raw[:16], raw[16:]
                pt = aes_cbc_decrypt(ct, iv)
            except Exception as exc:
                return self._send(400, f"bad token: {exc}\n")
            if pt.decode(errors="replace") == "role=admin":
                return self._send(200, f"admin ok; key={CHALLENGE_KEY}\n")
            return self._send(403, f"denied: {pt!r}\n")
        self._send(200, "CBC bit-flip: /token  /admin?token=  /flag\n")


def main():
    _MAT.update(fetch_material())
    print('CBC Bit Flip on :8080')
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

if __name__ == "__main__":
    main()
