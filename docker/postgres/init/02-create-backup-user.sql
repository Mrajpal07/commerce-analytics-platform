-- ============================================================================
-- Create Backup User (Production-Ready Setup)
-- ============================================================================
-- Creates a read-only user for backups and analytics
-- ============================================================================

-- Create backup/read-only user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'readonly_user') THEN
        CREATE ROLE readonly_user WITH LOGIN PASSWORD 'readonly_password_change_me';
    END IF;
END
$$;

-- Grant connect privilege
GRANT CONNECT ON DATABASE commerce_analytics TO readonly_user;

-- Grant usage on schemas
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT USAGE ON SCHEMA analytics TO readonly_user;

-- Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO readonly_user;

-- Grant SELECT on all future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO readonly_user;

-- Grant usage on sequences (needed for reading sequences)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO readonly_user;

COMMENT ON ROLE readonly_user IS 'Read-only user for backups and analytics';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Backup user created: readonly_user';
    RAISE NOTICE 'IMPORTANT: Change the password in production!';
END $$;
