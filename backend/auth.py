"""Password hashing, session cookies, and login rate limiting for the Campus Customs API.

Passwords are never stored or logged. Only a salted, slow PBKDF2-SHA256 hash goes into
users.password_hash. Sessions are signed cookies the browser cannot read or forge.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections import defaultdict, deque

# --- Password hashing -------------------------------------------------------------------

ALGORITHM = "pbkdf2_sha256"
# Assignment spec (Problem 4): PBKDF2-HMAC-SHA256, 120,000 iterations, stored as
# "pbkdf2_sha256$<salt>$<hex digest>". Signup and login use these identical settings, which also
# match the seeded accounts. Each guess against a stolen database costs 120,000 rounds.
ITERATIONS = 120_000
# Accounts created during development used "pbkdf2_sha256$600000$<salt>$<hex>"; still verifiable.
EXTENDED_FORMAT_PARTS = 4


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()


def hash_password(password: str) -> str:
    """Return "pbkdf2_sha256$<salt>$<hex digest>" with a fresh random 16-character salt."""
    salt = secrets.token_hex(8)
    return f"{ALGORITHM}${salt}${_pbkdf2(password, salt, ITERATIONS)}"


def verify_password(password: str, stored: str) -> bool:
    """Read the salt from the stored string, hash the typed password with it, compare in constant time."""
    parts = stored.split("$")
    if len(parts) == 3 and parts[0] == ALGORITHM:
        _, salt, expected = parts
        rounds = ITERATIONS
    elif len(parts) == EXTENDED_FORMAT_PARTS and parts[0] == ALGORITHM and parts[1].isdigit():
        _, iterations, salt, expected = parts
        rounds = int(iterations)
    else:
        return False
    # Constant-time comparison so response timing does not leak how close a guess was.
    return hmac.compare_digest(_pbkdf2(password, salt, rounds), expected)


# Used when an email is not registered, so unknown and known emails take the same time
# to reject and an attacker cannot tell which emails have accounts.
DUMMY_HASH = hash_password(secrets.token_urlsafe(16))


# --- Session cookies -------------------------------------------------------------------

SESSION_COOKIE = "cc_session"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60

_secret = os.getenv("SESSION_SECRET")
if not _secret:
    # Fine for local development: sessions simply end when the server restarts.
    _secret = secrets.token_urlsafe(32)
SESSION_SECRET = _secret.encode()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sign(payload: str) -> str:
    return _b64(hmac.new(SESSION_SECRET, payload.encode(), hashlib.sha256).digest())


def make_session_token(user_id: int) -> str:
    payload = _b64(json.dumps({"uid": user_id, "exp": int(time.time()) + SESSION_TTL_SECONDS}).encode())
    return f"{payload}.{_sign(payload)}"


def read_session_token(token: str | None) -> int | None:
    """Return the user id for a valid, unexpired token; None for anything tampered or stale."""
    if not token or "." not in token:
        return None
    payload, signature = token.rsplit(".", 1)
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    try:
        data = json.loads(_unb64(payload))
    except ValueError:
        return None
    if data.get("exp", 0) < time.time():
        return None
    return data.get("uid")


# --- Login rate limiting ------------------------------------------------------------------

MAX_FAILURES = 5
WINDOW_SECONDS = 15 * 60
_failures: dict[str, deque[float]] = defaultdict(deque)


def _recent(key: str) -> deque[float]:
    attempts = _failures[key]
    cutoff = time.time() - WINDOW_SECONDS
    while attempts and attempts[0] < cutoff:
        attempts.popleft()
    return attempts


def too_many_failures(*keys: str) -> bool:
    return any(len(_recent(k)) >= MAX_FAILURES for k in keys)


def record_failure(*keys: str) -> None:
    now = time.time()
    for k in keys:
        _recent(k).append(now)


def clear_failures(*keys: str) -> None:
    for k in keys:
        _failures.pop(k, None)
