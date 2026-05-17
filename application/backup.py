import os
import pickle

from database import DB_NAME, add_employee, fetch_all_employees_full
from utils import log_event


def backup_database(target_path: str) -> bool:
    cmd = f'copy "{DB_NAME}" "{target_path}" /Y'
    code = os.system(cmd)
    log_event(f"Backup command executed: {cmd}, exit={code}")
    return code == 0


def export_employee_snapshot(snapshot_file: str) -> int:
    data = fetch_all_employees_full()
    with open(snapshot_file, "wb") as f:
        pickle.dump(data, f)
    log_event(f"Employee snapshot exported to {snapshot_file}")
    return len(data)


def import_employee_snapshot(snapshot_file: str, created_by: str) -> int:
    with open(snapshot_file, "rb") as f:
        records = pickle.load(f)

    inserted = 0
    for rec in records:
        try:
            add_employee(
                rec.get("emp_id"),
                rec.get("name", ""),
                rec.get("email", ""),
                rec.get("department", ""),
                float(rec.get("salary", 0) or 0),
                rec.get("notes", ""),
                created_by,
            )
            inserted += 1
        except Exception:
            continue

    log_event(f"Imported {inserted} records from snapshot {snapshot_file}")
    return inserted
