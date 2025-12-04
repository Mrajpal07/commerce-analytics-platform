#!/bin/bash
# ============================================================================
# Setup Verification Script
# ============================================================================
# This script verifies that the PostgreSQL setup is complete and working
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Commerce Analytics Platform - Setup Verification${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check Docker
echo -e "${YELLOW}Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker installed${NC}"
    docker --version
else
    echo -e "${RED}✗ Docker not found!${NC}"
    exit 1
fi

# Check Docker Compose
echo -e "\n${YELLOW}Checking Docker Compose...${NC}"
if docker-compose --version &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
    docker-compose --version
else
    echo -e "${RED}✗ Docker Compose not found!${NC}"
    exit 1
fi

# Check containers
echo -e "\n${YELLOW}Checking containers...${NC}"
if docker ps | grep -q "commerce-analytics-postgres"; then
    echo -e "${GREEN}✓ PostgreSQL container running${NC}"
else
    echo -e "${RED}✗ PostgreSQL container not running!${NC}"
    echo "Run: docker-compose up -d postgres"
    exit 1
fi

if docker ps | grep -q "commerce-analytics-redis"; then
    echo -e "${GREEN}✓ Redis container running${NC}"
else
    echo -e "${RED}✗ Redis container not running!${NC}"
    echo "Run: docker-compose up -d redis"
    exit 1
fi

# Check PostgreSQL connection
echo -e "\n${YELLOW}Testing PostgreSQL connection...${NC}"
if docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
else
    echo -e "${RED}✗ Cannot connect to PostgreSQL!${NC}"
    exit 1
fi

# Check extensions
echo -e "\n${YELLOW}Checking PostgreSQL extensions...${NC}"
EXTENSIONS=$(docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -t -c "\dx" | grep -E "(uuid-ossp|pgcrypto|pg_trgm|btree_gin|btree_gist)" | wc -l)
if [ "$EXTENSIONS" -ge 5 ]; then
    echo -e "${GREEN}✓ All required extensions installed ($EXTENSIONS/5)${NC}"
    docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "\dx"
else
    echo -e "${RED}✗ Missing extensions! Found $EXTENSIONS/5${NC}"
fi

# Check schemas
echo -e "\n${YELLOW}Checking database schemas...${NC}"
SCHEMAS=$(docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -t -c "\dn" | grep -E "(public|analytics)" | wc -l)
if [ "$SCHEMAS" -ge 2 ]; then
    echo -e "${GREEN}✓ Required schemas exist ($SCHEMAS/2)${NC}"
else
    echo -e "${RED}✗ Missing schemas! Found $SCHEMAS/2${NC}"
fi

# Check tables
echo -e "\n${YELLOW}Checking database tables...${NC}"
TABLES=$(docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -t -c "\dt" | grep -E "(tenants|customers|orders|line_items|events|users)" | wc -l)
if [ "$TABLES" -ge 6 ]; then
    echo -e "${GREEN}✓ All application tables exist ($TABLES/6)${NC}"
    docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -c "\dt"
else
    echo -e "${RED}✗ Missing tables! Found $TABLES/6${NC}"
    echo "Run: python -m alembic upgrade head"
fi

# Check Alembic version
echo -e "\n${YELLOW}Checking Alembic migration status...${NC}"
if python -m alembic current &> /dev/null; then
    echo -e "${GREEN}✓ Alembic migrations applied${NC}"
    python -m alembic current
else
    echo -e "${RED}✗ Alembic migrations not applied!${NC}"
    echo "Run: python -m alembic upgrade head"
fi

# Check custom functions
echo -e "\n${YELLOW}Checking custom database functions...${NC}"
FUNCTIONS=$(docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -t -c "\df update_updated_at_column" | wc -l)
if [ "$FUNCTIONS" -ge 1 ]; then
    echo -e "${GREEN}✓ Custom functions installed${NC}"
else
    echo -e "${RED}✗ Custom functions missing!${NC}"
fi

# Check Redis connection
echo -e "\n${YELLOW}Testing Redis connection...${NC}"
if docker exec commerce-analytics-redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✓ Redis connection successful${NC}"
else
    echo -e "${RED}✗ Cannot connect to Redis!${NC}"
fi

# Database size
echo -e "\n${YELLOW}Database information...${NC}"
DB_SIZE=$(docker exec commerce-analytics-postgres psql -U user -d commerce_analytics -t -c "SELECT pg_size_pretty(pg_database_size('commerce_analytics'));")
echo -e "Database size: ${GREEN}$DB_SIZE${NC}"

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup verification completed!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo "Next steps:"
echo "  1. Start API: docker-compose up -d api"
echo "  2. View logs: docker-compose logs -f"
echo "  3. Access pgAdmin: http://localhost:5050"
echo "  4. Read: DATABASE_SETUP.md for more info"
