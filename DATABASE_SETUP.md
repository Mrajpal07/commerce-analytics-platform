# Database Setup Guide

This guide covers the production-ready PostgreSQL setup for the Commerce Analytics Platform.

## Quick Start

### Start Database

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f postgres
```

### Run Migrations

```bash
# Apply all migrations
python -m alembic upgrade head

# Check current version
python -m alembic current

# View migration history
python -m alembic history
```

## Production Setup

### 1. Environment Configuration

Copy the production environment template:

```bash
cp .env.production .env
```

**IMPORTANT:** Update the following values in `.env`:

- `DATABASE_URL` - Change password from default
- `JWT_SECRET_KEY` - Generate new: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `FERNET_ENCRYPTION_KEY` - Generate new: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `CORS_ORIGINS` - Set your production domains
- `SENTRY_DSN` - Add your Sentry project DSN

### 2. Start Production Stack

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check health
docker-compose -f docker-compose.prod.yml ps
```

## Database Features

### Extensions Installed

- **uuid-ossp** - UUID generation
- **pgcrypto** - Cryptographic functions
- **pg_trgm** - Trigram matching for fuzzy search
- **btree_gin** - GIN indexes for btree types
- **btree_gist** - GIST indexes for btree types

### Custom Functions

- `update_updated_at_column()` - Automatically updates `updated_at` timestamps
- `set_tenant_context(tenant_id)` - Sets tenant context for Row-Level Security

### Schemas

- **public** - Main application tables
- **analytics** - Analytics and reporting views

## Database Management

### Access Database

```bash
# Using Docker
docker exec -it commerce-analytics-postgres psql -U user -d commerce_analytics

# List all tables
\dt

# Describe table structure
\d tenants

# List extensions
\dx

# List schemas
\dn+
```

### Backup Database

```bash
# Create backup
./scripts/backup-postgres.sh

# Backups are stored in ./backups/postgres/
# Format: backup_commerce_analytics_YYYYMMDD_HHMMSS.sql.gz
# Retention: 7 days (automatically cleaned)
```

### Restore Database

```bash
# Restore from backup
./scripts/restore-postgres.sh ./backups/postgres/backup_commerce_analytics_20231215_120000.sql.gz

# WARNING: This will replace all current data!
```

### Make Scripts Executable

```bash
chmod +x scripts/backup-postgres.sh
chmod +x scripts/restore-postgres.sh
```

## Migrations

### Create New Migration

```bash
# Auto-generate migration from model changes
python -m alembic revision --autogenerate -m "description_of_changes"

# Create empty migration (manual)
python -m alembic revision -m "description_of_changes"
```

### Apply Migrations

```bash
# Upgrade to latest version
python -m alembic upgrade head

# Upgrade to specific version
python -m alembic upgrade <revision_id>

# Upgrade by +N versions
python -m alembic upgrade +2
```

### Rollback Migrations

```bash
# Downgrade by one version
python -m alembic downgrade -1

# Downgrade to specific version
python -m alembic downgrade <revision_id>

# Downgrade to base (removes all)
python -m alembic downgrade base
```

### Migration History

```bash
# View current version
python -m alembic current

# View migration history
python -m alembic history

# View detailed history
python -m alembic history --verbose
```

## Performance Tuning

### Configuration Highlights

The PostgreSQL configuration is optimized for:

- **Memory**: 1GB RAM system (adjust in [postgresql.conf](docker/postgres/conf/postgresql.conf))
- **Storage**: SSD-optimized (`random_page_cost = 1.1`)
- **Connections**: Max 100 concurrent connections
- **Query Timeout**: 30 seconds default
- **Logging**: Queries slower than 1 second

### Monitoring

```bash
# Check slow queries
docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "SELECT * FROM analytics.slow_queries;"

# Check connection count
docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "SELECT count(*) FROM pg_stat_activity;"

# Check database size
docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "SELECT pg_size_pretty(pg_database_size('commerce_analytics'));"

# Check table sizes
docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "\dt+"
```

## Troubleshooting

### Connection Refused

**Problem**: `connection to server at "localhost", port 5432 failed: Connection refused`

**Solution**:
```bash
# Check if container is running
docker-compose ps

# Start if not running
docker-compose up -d postgres

# Check logs for errors
docker-compose logs postgres
```

### Migration Conflicts

**Problem**: Migration already exists or conflicts

**Solution**:
```bash
# Check current version
python -m alembic current

# View all migrations
python -m alembic history

# If needed, downgrade and re-apply
python -m alembic downgrade -1
python -m alembic upgrade head
```

### Database Corruption

**Problem**: Database won't start or data is corrupted

**Solution**:
```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: destroys all data)
docker-compose down -v

# Restore from backup
docker-compose up -d postgres
./scripts/restore-postgres.sh ./backups/postgres/latest_backup.sql.gz
```

### Slow Queries

**Problem**: Database queries are slow

**Solution**:
```bash
# Enable query logging
# Edit postgresql.conf: log_min_duration_statement = 100

# Analyze query performance
docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "EXPLAIN ANALYZE SELECT * FROM orders WHERE tenant_id = 1;"

# Run VACUUM ANALYZE
docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "VACUUM ANALYZE;"
```

## Security Best Practices

### Production Checklist

- [ ] Change default database password
- [ ] Enable SSL/TLS for PostgreSQL connections
- [ ] Set up Row-Level Security (RLS) policies
- [ ] Configure firewall rules (only allow necessary IPs)
- [ ] Enable PostgreSQL audit logging
- [ ] Rotate backup encryption keys
- [ ] Set up automated backups to remote storage
- [ ] Configure database replication for high availability
- [ ] Implement connection pooling (PgBouncer)
- [ ] Monitor with Prometheus/Grafana

### Row-Level Security (RLS)

Enable RLS for tenant isolation:

```sql
-- Enable RLS on tables
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE line_items ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY tenant_isolation_orders ON orders
  USING (tenant_id = current_setting('app.current_tenant_id')::integer);

CREATE POLICY tenant_isolation_customers ON customers
  USING (tenant_id = current_setting('app.current_tenant_id')::integer);

CREATE POLICY tenant_isolation_line_items ON line_items
  USING (tenant_id = current_setting('app.current_tenant_id')::integer);
```

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Support

For issues or questions:
1. Check logs: `docker-compose logs postgres`
2. Review this guide
3. Check PostgreSQL documentation
4. Open an issue in the project repository
