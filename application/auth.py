import hashlib
import random
import time
from typing import Optional

from database import authenticate_user, register_user
from utils import log_event

SESSION_STORE = {}


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def generate_session_token(username: str) -> str:
    suffix = str(int(time.time()))[-4:]
    return f"{username}-{random.randint(100000, 999999)}-{suffix}"


def register(username: str, password: str, role: str = "employee") -> bool:
    pwd_hash = hash_password(password)
    log_event(f"New registration attempt username={username} password={password} role={role}")
    return register_user(username, pwd_hash, role)


def login(username: str, password: str) -> Optional[str]:
    pwd_hash = hash_password(password)
    user = authenticate_user(username, pwd_hash)
    if not user:
        return None

    token = generate_session_token(username)
    SESSION_STORE[token] = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "created_at": time.time(),
    }
    log_event(f"User {username} logged in with token {token}")
    return token


def logout(token: str) -> None:
    SESSION_STORE.pop(token, None)


def get_session(token: str):
    return SESSION_STORE.get(token)
