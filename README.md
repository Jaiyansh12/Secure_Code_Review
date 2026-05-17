# Secure Coding Review - Employee Management System

## About The Project

This project was completed as part of a Cyber Security Internship task focused on Secure Coding Review.

The repository contains a Python-based Employee Management System application along with a manual security assessment report documenting identified vulnerabilities, security risks, and remediation recommendations.

The application was generated using AI-assisted development tools and manually reviewed to analyze insecure coding practices and application security issues.

---

## Features

- User registration and login system
- Employee record management
- Administrative functionalities
- Database operations using SQLite
- File upload and file viewing functionality
- Backup and snapshot handling

---

## Technologies Used

- Python
- SQLite
- Logging
- File Handling
- Pickle Serialization

---

## Project Structure

```text
CodeAlpha_Secure_Coding_Review/
│
├── application/
│   ├── auth.py
│   ├── backup.py
│   ├── database.py
│   ├── main.py
│   ├── utils.py
│   ├── employee_mgmt.db
│   └── app.log
│
├── reports/
│   └── security_review_report.md
│
├── screenshots/
│
└── README.md
```

---

## Security Review

The secure coding review report is available inside:

```text
reports/security_review_report.md
```

The report includes:
- Identified vulnerabilities
- Risk analysis
- Severity classification
- Vulnerable code snippets
- Remediation recommendations

---

## How To Run

1. Open terminal in the project directory
2. Navigate to the application folder

```bash
cd application
```

3. Run the application

```bash
python main.py
```

---
