-- ============================================================================
-- PostgreSQL Initialization Script
-- Commerce Analytics Platform
-- ============================================================================
-- This script runs automatically when the PostgreSQL container first starts
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";       -- Cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Trigram matching for fuzzy search
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- GIN indexes for btree types
CREATE EXTENSION IF NOT EXISTS "btree_gist";     -- GIST indexes for btree types

-- Create custom schema for separation
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set default schema search path
ALTER DATABASE commerce_analytics SET search_path TO public, analytics;

-- ============================================================================
-- PERFORMANCE: Create indexes that will be used across tables
-- ============================================================================

-- Note: Table-specific indexes will be created by Alembic migrations
-- This section is for global utilities

-- ============================================================================
-- SECURITY: Row-Level Security (RLS) Setup
-- ============================================================================

-- Enable RLS on tables (will be applied to tenant-specific tables)
-- This is a template for RLS policies that will be applied after table creation

-- Example RLS policy (to be applied after tables are created):
-- ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY tenant_isolation ON orders
--   USING (tenant_id = current_setting('app.current_tenant_id')::integer);

-- ============================================================================
-- CUSTOM FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to safely set tenant context
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_id_param INTEGER)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', tenant_id_param::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- MONITORING: Statistics and Performance Views
-- ============================================================================

-- Create a view for monitoring slow queries
CREATE OR REPLACE VIEW analytics.slow_queries AS
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- Queries slower than 1 second
ORDER BY mean_exec_time DESC
LIMIT 20;

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant usage on schemas
GRANT USAGE ON SCHEMA public TO user;
GRANT USAGE ON SCHEMA analytics TO user;

-- Grant all privileges on current and future tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO user;

-- ============================================================================
-- COMMENTS (Documentation)
-- ============================================================================

COMMENT ON EXTENSION "uuid-ossp" IS 'UUID generation functions';
COMMENT ON EXTENSION "pgcrypto" IS 'Cryptographic functions for password hashing';
COMMENT ON EXTENSION "pg_trgm" IS 'Trigram matching for fuzzy text search';
COMMENT ON SCHEMA analytics IS 'Schema for analytics and reporting views';
COMMENT ON FUNCTION update_updated_at_column() IS 'Trigger function to automatically update updated_at timestamp';
COMMENT ON FUNCTION set_tenant_context(INTEGER) IS 'Set current tenant context for RLS policies';

-- ============================================================================
-- VACUUM AND ANALYZE
-- ============================================================================

-- Initial vacuum analyze (optional, as autovacuum will handle this)
VACUUM ANALYZE;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '=======================================================';
    RAISE NOTICE 'Commerce Analytics Platform Database Initialized';
    RAISE NOTICE 'Database: commerce_analytics';
    RAISE NOTICE 'Extensions: uuid-ossp, pgcrypto, pg_trgm, btree_gin, btree_gist';
    RAISE NOTICE 'Schemas: public, analytics';
    RAISE NOTICE '=======================================================';
END $$;
