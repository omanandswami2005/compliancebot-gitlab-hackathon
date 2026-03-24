"""
Payment processing service for handling customer transactions.
WARNING: This file contains intentional compliance violations for demo purposes.
"""

import hashlib
import sqlite3
import requests

# VIOLATION: Hardcoded API keys and secrets
STRIPE_API_KEY = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"
DATABASE_PASSWORD = "admin123!"
JWT_SECRET = "my-super-secret-jwt-key-2026"

# VIOLATION: Hardcoded PII encryption key
ENCRYPTION_KEY = "AES256-KEY-DO-NOT-SHARE-12345678"


class PaymentProcessor:
    """Handles payment transactions."""

    def __init__(self):
        self.db = sqlite3.connect("payments.db")
        self.api_key = STRIPE_API_KEY

    def process_payment(self, user_id, amount, card_number):
        """Process a credit card payment."""

        # VIOLATION: SQL Injection - string concatenation in query
        cursor = self.db.cursor()
        query = f"SELECT * FROM users WHERE id = '{user_id}'"
        cursor.execute(query)
        user = cursor.fetchone()

        # VIOLATION: Logging sensitive PCI data (card numbers)
        print(f"Processing payment for user {user_id}, card: {card_number}, amount: ${amount}")

        # VIOLATION: Storing card number in plain text
        insert_query = f"INSERT INTO transactions (user_id, card_number, amount) VALUES ('{user_id}', '{card_number}', {amount})"
        cursor.execute(insert_query)
        self.db.commit()

        # VIOLATION: Using MD5 for hashing (weak encryption)
        transaction_hash = hashlib.md5(f"{user_id}{amount}".encode()).hexdigest()

        return {"status": "success", "hash": transaction_hash}

    def get_patient_records(self, patient_id):
        """Retrieve patient health records."""

        # VIOLATION: No access control check on health data (HIPAA)
        cursor = self.db.cursor()
        query = f"SELECT * FROM patient_records WHERE patient_id = '{patient_id}'"
        cursor.execute(query)

        # VIOLATION: Returning PHI without encryption or audit logging
        records = cursor.fetchall()
        return records

    def send_to_webhook(self, url, data):
        """Forward transaction data to webhook."""

        # VIOLATION: SSL verification disabled
        response = requests.post(url, json=data, verify=False)
        return response.json()


def authenticate_user(username, password):
    """Authenticate a user with username and password."""

    # VIOLATION: SQL injection in authentication
    db = sqlite3.connect("payments.db")
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

    user = cursor.fetchone()
    if user:
        # VIOLATION: Using SHA1 (weak hash) for session token
        session_token = hashlib.sha1(f"{username}{password}".encode()).hexdigest()
        return {"authenticated": True, "token": session_token}

    return {"authenticated": False}
