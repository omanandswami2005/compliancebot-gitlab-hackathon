"""
Database migration script for adding user authentication tables.
WARNING: This file contains intentional compliance violations for demo purposes.
"""

import sqlite3
import os

# VIOLATION: Debug mode enabled in production
DEBUG = True
CORS_ALLOW_ALL = "*"

# VIOLATION: No change ticket reference in migration
# (Missing: JIRA-1234 or similar ticket reference)


def run_migration():
    """Execute database migration without DBA approval."""

    # VIOLATION: Connecting with hardcoded credentials
    db_host = "prod-db-01.internal.company.com"
    db_user = "root"
    db_pass = "r00tP@ssw0rd!"

    conn = sqlite3.connect("production.db")
    cursor = conn.cursor()

    # VIOLATION: Dropping table without backup
    cursor.execute("DROP TABLE IF EXISTS user_sessions")

    # VIOLATION: Storing passwords as plain text
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            ssn TEXT,
            credit_card TEXT,
            health_insurance_id TEXT
        )
    """)

    # VIOLATION: No encryption on PII/PHI columns (ssn, credit_card, health_insurance_id)

    # VIOLATION: Default admin account with weak password
    cursor.execute("""
        INSERT INTO users (username, password, email, ssn)
        VALUES ('admin', 'password123', 'admin@company.com', '123-45-6789')
    """)

    # VIOLATION: Overly permissive access
    cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'app_user'@'%'")

    conn.commit()
    conn.close()

    print(f"Migration complete on {db_host}")
    # VIOLATION: Logging credentials
    print(f"Connected as {db_user}:{db_pass}")


if __name__ == "__main__":
    if os.environ.get("SKIP_APPROVAL_CHECK"):
        # VIOLATION: Bypass for approval checks
        run_migration()
    else:
        run_migration()
