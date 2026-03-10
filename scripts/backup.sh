#!/bin/bash
# QA-FRAMEWORK - Database Backup Script

set -e

echo "💾 QA-FRAMEWORK Database Backup"
echo "Started: $(date)"
echo ""

# Configuration
BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Database connection (from environment)
DATABASE_URL="${DATABASE_URL:-}"

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Creating backup..."
echo "File: $BACKUP_FILE"

# Parse DATABASE_URL
# Format: postgresql://user:password@host:port/database
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

# Create backup using pg_dump
PGPASSWORD=$DB_PASS pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    -F p \
    -f $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo ""
echo "✅ Backup completed successfully!"
echo "File: ${BACKUP_FILE}.gz"
echo "Size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo ""
echo "Old backups cleaned (keeping last 7 days)"
echo "Finished: $(date)"
