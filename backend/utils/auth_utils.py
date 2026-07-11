from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode('ascii')


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def jwt_encode(payload: Dict[str, Any], secret: str, expire_seconds: int = 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = dict(payload)
    payload.setdefault("iat", int(time.time()))
    payload.setdefault("exp", int(time.time()) + int(expire_seconds))

    header_b = _b64url_encode(json.dumps(header, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))
    payload_b = _b64url_encode(json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))
    signing_input = f"{header_b}.{payload_b}".encode('ascii')
    sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b = _b64url_encode(sig)
    return f"{header_b}.{payload_b}.{sig_b}"


def jwt_decode(token: str, secret: str) -> Dict[str, Any]:
    try:
        header_b, payload_b, sig_b = token.split('.')
    except ValueError:
        raise ValueError('invalid token')

    signing_input = f"{header_b}.{payload_b}".encode('ascii')
    expected_sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, _b64url_decode(sig_b)):
        raise ValueError('invalid signature')

    payload_json = _b64url_decode(payload_b)
    payload = json.loads(payload_json.decode('utf-8'))
    exp = payload.get('exp')
    if exp is not None and int(time.time()) > int(exp):
        raise ValueError('token expired')
    return payload


def generate_token_for_user(user_id: Any, secret: str, expire_seconds: int = 3600, extra: Optional[Dict[str, Any]] = None) -> str:
    payload = {"sub": str(user_id)}
    if extra:
        payload.update(extra)
    return jwt_encode(payload, secret, expire_seconds=expire_seconds)


def verify_token(token: str, secret: str) -> Dict[str, Any]:
    return jwt_decode(token, secret)


def _random_salt(n: int = 16) -> bytes:
    return os.urandom(n)


def hash_password(password: str, salt: Optional[bytes] = None, iterations: int = 120000) -> str:
    """使用 PBKDF2-HMAC-SHA256 对密码加盐哈希，返回格式：iterations$salt_hex$hash_hex"""
    if salt is None:
        salt = _random_salt()
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f"{iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        iterations_str, salt_hex, hash_hex = stored.split('$')
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
    except Exception:
        return False
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return hmac.compare_digest(dk.hex(), hash_hex)
