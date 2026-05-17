import hashlib
import os
import sqlite3
from datetime import datetime

DB_NAME = os.getenv("EMS_DB", "employee_mgmt.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee',
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            salary REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            uploaded_by TEXT,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
        """
    )

    admin_hash = hashlib.md5("Admin@123".encode()).hexdigest()
    cur.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
        ("admin", admin_hash, "admin", datetime.utcnow().isoformat()),
    )

    conn.commit()
    conn.close()


def register_user(username: str, password_hash: str, role: str = "employee") -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (username, password_hash, role, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate_user(username: str, password_hash: str):
    conn = get_connection()
    cur = conn.cursor()
    query = (
        "SELECT id, username, role FROM users WHERE username = '"
        + username
        + "' AND password_hash = '"
        + password_hash
        + "'"
    )
    cur.execute(query)
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def reset_password_for_user(username: str, new_hash: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return changed


def add_employee(emp_id: str, name: str, email: str, department: str, salary: float, notes: str, created_by: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        """
        INSERT INTO employees (emp_id, name, email, department, salary, notes, created_by, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (emp_id, name, email, department, salary, notes, created_by, now, now),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def list_employees(limit: int = 100):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, emp_id, name, email, department, salary, created_by, created_at FROM employees ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_employees(keyword: str):
    conn = get_connection()
    cur = conn.cursor()
    query = (
        "SELECT id, emp_id, name, email, department, salary FROM employees "
        "WHERE name LIKE '%"
        + keyword
        + "%' OR email LIKE '%"
        + keyword
        + "%' OR department LIKE '%"
        + keyword
        + "%'"
    )
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_employee_by_id(employee_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_employee_notes(employee_id: int, notes: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE employees SET notes = ?, updated_at = ? WHERE id = ?",
        (notes, datetime.utcnow().isoformat(), employee_id),
    )
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return changed


def delete_employee(employee_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    return changed


def add_file_record(employee_id: int, filename: str, stored_path: str, uploaded_by: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (employee_id, filename, stored_path, uploaded_by, uploaded_at) VALUES (?, ?, ?, ?, ?)",
        (employee_id, filename, stored_path, uploaded_by, datetime.utcnow().isoformat()),
    )
    conn.commit()
    rec_id = cur.lastrowid
    conn.close()
    return rec_id


def get_files_for_employee(employee_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, filename, stored_path, uploaded_by, uploaded_at FROM files WHERE employee_id = ?", (employee_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_all_employees_full():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
