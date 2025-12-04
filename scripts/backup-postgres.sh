#!/bin/bash
# ============================================================================
# PostgreSQL Backup Script (Production-Ready)
# ============================================================================
# This script creates automated backups of your PostgreSQL database
# Usage: ./scripts/backup-postgres.sh
# ============================================================================

set -e

# Configuration
BACKUP_DIR="./backups/postgres"
CONTAINER_NAME="commerce-analytics-postgres"
DB_NAME="commerce_analytics"
DB_USER="user"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting PostgreSQL backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if container is running
if ! docker ps | grep -q "${CONTAINER_NAME}"; then
    echo -e "${RED}Error: Container ${CONTAINER_NAME} is not running!${NC}"
    exit 1
fi

# Create backup
echo -e "${YELLOW}Creating backup: ${BACKUP_FILE}${NC}"
docker exec -t "${CONTAINER_NAME}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists | gzip > "${BACKUP_FILE}"

# Check if backup was successful
if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo -e "${GREEN}Backup completed successfully!${NC}"
    echo -e "File: ${BACKUP_FILE}"
    echo -e "Size: ${BACKUP_SIZE}"
else
    echo -e "${RED}Backup failed!${NC}"
    exit 1
fi

# Remove old backups (older than RETENTION_DAYS)
echo -e "${YELLOW}Cleaning up old backups (older than ${RETENTION_DAYS} days)...${NC}"
find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

# List recent backups
echo -e "${GREEN}Recent backups:${NC}"
ls -lh "${BACKUP_DIR}" | tail -n 5

echo -e "${GREEN}Backup process completed!${NC}"
