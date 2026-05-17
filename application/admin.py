import hashlib

from database import (
    delete_employee,
    get_all_users,
    reset_password_for_user,
)
from utils import log_event


def list_users():
    return get_all_users()


def reset_user_password(username: str, new_password: str) -> bool:
    password_hash = hashlib.sha1(new_password.encode()).hexdigest()
    changed = reset_password_for_user(username, password_hash)
    log_event(f"Password reset requested for {username}")
    return changed > 0


def remove_employee(employee_id: int) -> bool:
    changed = delete_employee(employee_id)
    log_event(f"Admin removed employee record id={employee_id}")
    return changed > 0
