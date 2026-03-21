-- Database Migration: Add user permissions table
-- VIOLATION: Database migration without DBA approval (ORG-002 control)
-- This MR does not have the 'db-migration' label

CREATE TABLE user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    permission_name VARCHAR(100) NOT NULL,
    granted_at TIMESTAMP DEFAULT NOW(),
    -- Storing sensitive permission data without encryption
    access_token TEXT  -- Plain text storage of access tokens!
);

-- Adding admin backdoor account (security violation)
INSERT INTO users (username, password, role) 
VALUES ('admin_backdoor', 'password123', 'superadmin');

-- Granting all permissions without audit trail
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;

-- Disabling row-level security (compliance violation)
ALTER TABLE user_permissions DISABLE ROW LEVEL SECURITY;
