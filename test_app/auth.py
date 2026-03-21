# Authentication module - COMPLIANCE TEST FILE
# This file contains intentional compliance violations for testing ComplianceBot

import hashlib
import os

# VIOLATION 1: Hardcoded API key (secret_detected - CRITICAL)
API_KEY = "sk-live-abc123xyz789secretkey"
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE+wJalrXUtnFEMI/K7MDENG/bPxRfiCY"

# VIOLATION 2: Weak encryption (encryption_change - HIGH)
def encrypt_password(password):
    """Using MD5 for password hashing - insecure!"""
    return hashlib.md5(password.encode()).hexdigest()

# VIOLATION 3: No input validation on auth (auth_change - HIGH)
def authenticate_user(username, password):
    """Direct SQL query without parameterization"""
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    # This is vulnerable to SQL injection
    return execute_query(query)

# VIOLATION 4: Session token with weak entropy
def generate_session_token():
    """Weak session token generation"""
    import random
    return str(random.randint(1000, 9999))  # Only 4 digits - easily guessable

# VIOLATION 5: Disabled SSL verification (encryption_change - CRITICAL)
def make_api_request(url):
    import requests
    # Disabling SSL verification is a security risk
    response = requests.get(url, verify=False)
    return response.json()

# VIOLATION 6: Logging sensitive data
def login(username, password):
    print(f"Login attempt: user={username}, pass={password}")  # Logging password!
    return authenticate_user(username, password)

# VIOLATION 7: JWT without expiration
def create_jwt_token(user_id):
    """Creating JWT without expiration - tokens never expire"""
    import jwt
    payload = {
        "user_id": user_id,
        # Missing 'exp' claim - token never expires
    }
    return jwt.encode(payload, API_KEY, algorithm="HS256")
