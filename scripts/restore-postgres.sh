#!/bin/bash
# ============================================================================
# PostgreSQL Restore Script (Production-Ready)
# ============================================================================
# This script restores a PostgreSQL database from a backup file
# Usage: ./scripts/restore-postgres.sh <backup_file>
# Example: ./scripts/restore-postgres.sh ./backups/postgres/backup_commerce_analytics_20231215_120000.sql.gz
# ============================================================================

set -e

# Configuration
CONTAINER_NAME="commerce-analytics-postgres"
DB_NAME="commerce_analytics"
DB_USER="user"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backup file argument is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Backup file not specified!${NC}"
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 ./backups/postgres/backup_commerce_analytics_20231215_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will restore the database from backup!${NC}"
echo -e "${YELLOW}All current data will be replaced!${NC}"
echo -e "Backup file: ${BACKUP_FILE}"
echo -e "Database: ${DB_NAME}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo -e "${RED}Restore cancelled.${NC}"
    exit 0
fi

# Check if container is running
if ! docker ps | grep -q "${CONTAINER_NAME}"; then
    echo -e "${RED}Error: Container ${CONTAINER_NAME} is not running!${NC}"
    exit 1
fi

echo -e "${GREEN}Starting restore process...${NC}"

# Restore backup
echo -e "${YELLOW}Restoring from: ${BACKUP_FILE}${NC}"
gunzip -c "${BACKUP_FILE}" | docker exec -i "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database restored successfully!${NC}"
else
    echo -e "${RED}Restore failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Restore process completed!${NC}"
