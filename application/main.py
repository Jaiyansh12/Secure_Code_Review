from auth import get_session, login, logout, register
from admin import list_users, remove_employee, reset_user_password
from backup import backup_database, export_employee_snapshot, import_employee_snapshot
from database import (
    add_employee,
    add_file_record,
    get_employee_by_id,
    get_files_for_employee,
    init_db,
    list_employees,
    search_employees,
    update_employee_notes,
)
from utils import log_event, prompt_int, read_file_contents, save_uploaded_file


CURRENT_TOKEN = None


def print_employee_rows(rows):
    if not rows:
        print("No records found.")
        return

    for row in rows:
        print(
            f"[{row.get('id')}] {row.get('emp_id')} | {row.get('name')} | {row.get('email')} "
            f"| {row.get('department')} | {row.get('salary')}"
        )


def handle_register():
    print("\n--- Register User ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    role = input("Role [employee/admin] (default employee): ").strip() or "employee"

    if register(username, password, role):
        print("User created successfully.")
    else:
        print("Failed to create user. Username may already exist.")


def handle_login():
    global CURRENT_TOKEN

    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    token = login(username, password)
    if not token:
        print("Invalid username or password.")
        return

    CURRENT_TOKEN = token
    print("Login successful.")


def require_session():
    if not CURRENT_TOKEN:
        print("Please login first.")
        return None

    session = get_session(CURRENT_TOKEN)
    if not session:
        print("Session expired or invalid. Please login again.")
        return None

    return session


def handle_add_employee(session):
    print("\n--- Add Employee ---")
    emp_id = input("Employee code (e.g. EMP-1001): ").strip()
    name = input("Full name: ").strip()
    email = input("Email: ").strip()
    department = input("Department: ").strip()
    salary = float(input("Salary: ").strip() or 0)
    notes = input("Notes: ").strip()

    try:
        row_id = add_employee(emp_id, name, email, department, salary, notes, session["username"])
        print(f"Employee created with record id {row_id}.")
    except Exception as exc:
        print(f"Failed to add employee: {exc}")


def handle_list_employees():
    print("\n--- Employee List ---")
    rows = list_employees()
    print_employee_rows(rows)


def handle_search_employee():
    print("\n--- Search Employees ---")
    keyword = input("Keyword: ").strip()
    rows = search_employees(keyword)
    print_employee_rows(rows)


def handle_update_notes():
    print("\n--- Update Employee Notes ---")
    employee_id = prompt_int("Employee record id: ")
    notes = input("New notes: ").strip()
    changed = update_employee_notes(employee_id, notes)
    print("Updated." if changed else "No employee updated.")


def handle_upload_file(session):
    print("\n--- Attach Employee File ---")
    employee_id = prompt_int("Employee record id: ")
    employee = get_employee_by_id(employee_id)
    if not employee:
        print("Employee not found.")
        return

    source = input("Source file path: ").strip()
    target_name = input("Store as name (optional): ").strip()

    try:
        stored_path = save_uploaded_file(source, target_name)
        rec_id = add_file_record(employee_id, target_name or source, stored_path, session["username"])
        print(f"File attached successfully. File record id: {rec_id}")
    except Exception as exc:
        print(f"Upload failed: {exc}")


def handle_view_file_contents():
    print("\n--- View Attached File Contents ---")
    file_path = input("File path under uploads: ").strip()
    try:
        print("\n----- FILE START -----")
        print(read_file_contents(file_path))
        print("----- FILE END -----")
    except Exception as exc:
        print(f"Failed to read file: {exc}")


def handle_admin_menu(session):
    if session["role"] != "admin":
        print("Admin access required.")
        return

    while True:
        print("\n=== Admin Menu ===")
        print("1. List users")
        print("2. Reset user password")
        print("3. Remove employee")
        print("4. Backup database")
        print("5. Export employee snapshot")
        print("6. Import employee snapshot")
        print("7. Back")

        choice = input("Select option: ").strip()

        if choice == "1":
            users = list_users()
            for user in users:
                print(f"[{user['id']}] {user['username']} ({user['role']}) created={user['created_at']}")

        elif choice == "2":
            username = input("Username to reset: ").strip()
            new_password = input("New password: ").strip()
            ok = reset_user_password(username, new_password)
            print("Password updated." if ok else "User not found.")

        elif choice == "3":
            employee_id = prompt_int("Employee id to remove: ")
            ok = remove_employee(employee_id)
            print("Removed." if ok else "Employee not found.")

        elif choice == "4":
            target = input("Backup target path (e.g. backups\\employees.db): ").strip()
            ok = backup_database(target)
            print("Backup completed." if ok else "Backup failed.")

        elif choice == "5":
            file_name = input("Snapshot file name (e.g. snapshots.bin): ").strip()
            count = export_employee_snapshot(file_name)
            print(f"Exported {count} records.")

        elif choice == "6":
            file_name = input("Snapshot file to import: ").strip()
            count = import_employee_snapshot(file_name, session["username"])
            print(f"Imported {count} records.")

        elif choice == "7":
            break

        else:
            print("Invalid option.")


def handle_logged_in_menu(session):
    while True:
        print(f"\n=== Employee Management ({session['username']} | {session['role']}) ===")
        print("1. Add employee")
        print("2. List employees")
        print("3. Search employees")
        print("4. Update employee notes")
        print("5. Attach document")
        print("6. View document contents")
        print("7. Admin menu")
        print("8. Logout")

        choice = input("Select option: ").strip()

        if choice == "1":
            handle_add_employee(session)
        elif choice == "2":
            handle_list_employees()
        elif choice == "3":
            handle_search_employee()
        elif choice == "4":
            handle_update_notes()
        elif choice == "5":
            handle_upload_file(session)
        elif choice == "6":
            handle_view_file_contents()
        elif choice == "7":
            handle_admin_menu(session)
        elif choice == "8":
            global CURRENT_TOKEN
            if CURRENT_TOKEN:
                logout(CURRENT_TOKEN)
            CURRENT_TOKEN = None
            print("Logged out.")
            return
        else:
            print("Invalid option.")


def main():
    init_db()
    log_event("Application started")

    while True:
        session = require_session() if CURRENT_TOKEN else None

        if session:
            handle_logged_in_menu(session)
            continue

        print("\n=== Employee Management System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Select option: ").strip()

        if choice == "1":
            handle_register()
        elif choice == "2":
            handle_login()
        elif choice == "3":
            print("Goodbye")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
