# Configuration file with security violations
# COMPLIANCE TEST - Multiple violations

# VIOLATION: Hardcoded database credentials (secret_detected - CRITICAL)
DATABASE_CONFIG = {
    "host": "prod-db.company.internal",
    "port": 5432,
    "database": "production_users",
    "username": "db_admin",
    "password": "SuperSecret123!@#",  # Hardcoded production password
}

# VIOLATION: Hardcoded encryption keys (secret_detected - CRITICAL)
ENCRYPTION_KEY = "aes-256-key-do-not-share-12345678901234567890"
JWT_SECRET = "my-super-secret-jwt-key-never-change"

# VIOLATION: Debug mode enabled in production
DEBUG = True
TESTING = True

# VIOLATION: Insecure cookie settings
SESSION_CONFIG = {
    "secure": False,  # Should be True for HTTPS
    "httponly": False,  # Should be True to prevent XSS
    "samesite": None,  # Should be 'Strict' or 'Lax'
}

# VIOLATION: Weak password policy
PASSWORD_POLICY = {
    "min_length": 4,  # Too short
    "require_uppercase": False,
    "require_numbers": False,
    "require_special": False,
}

# VIOLATION: Overly permissive CORS
CORS_ORIGINS = ["*"]  # Allows any origin

# VIOLATION: Disabled security headers
SECURITY_HEADERS = {
    "X-Frame-Options": None,  # Clickjacking vulnerability
    "X-Content-Type-Options": None,
    "Content-Security-Policy": None,
}

# Private key embedded in code (CRITICAL)
PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7MmE8DmWpS8QXZZZZ
kljsdflkjsdfkljsdflkjsdfkljsdfkljsdfkljsdfkljsdfkljsdfkljsdfkljsd
-----END RSA PRIVATE KEY-----
"""
