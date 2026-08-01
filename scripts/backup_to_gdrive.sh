#!/usr/bin/env bash
# ==============================================================================
# 🗄️ Automated Database Backup to Google Drive (via rclone)
# ==============================================================================
# Usage: ./scripts/backup_to_gdrive.sh
# Can be scheduled via cron (e.g. 0 2 * * * for daily at 2:00 AM)
# ==============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${BACKEND_DIR}/database_backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RCLONE_REMOTE="gdrive:Portfolio_Backups"  # Matches rclone remote name and folder

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] 📦 Starting database backup process..."

# 1. Determine DB source (SQLite portfolio.db or export)
DB_FILE="${BACKEND_DIR}/portfolio.db"
BACKUP_FILE="${BACKUP_DIR}/portfolio_backup_${TIMESTAMP}.db"

if [ -f "${DB_FILE}" ]; then
    echo "[$(date)] ⚙️ Backing up SQLite database..."
    # Use sqlite3 .backup if available for safe online backup, fallback to cp
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "${DB_FILE}" ".backup '${BACKUP_FILE}'"
    else
        cp "${DB_FILE}" "${BACKUP_FILE}"
    fi
else
    echo "[$(date)] ⚠️ ${DB_FILE} not found. Running seed/export script if applicable..."
    python3 "${BACKEND_DIR}/scripts/seed.py" --export "${BACKUP_FILE}" 2>/dev/null || true
fi

# Compress backup
if [ -f "${BACKUP_FILE}" ]; then
    gzip -f "${BACKUP_FILE}"
    ZIPPED_BACKUP="${BACKUP_FILE}.gz"
    echo "[$(date)] ✅ Created compressed backup: ${ZIPPED_BACKUP}"
else
    echo "[$(date)] ❌ Backup file generation failed."
    exit 1
fi

# 2. Upload to Google Drive using rclone
if command -v rclone >/dev/null 2>&1; then
    echo "[$(date)] 🚀 Uploading to Google Drive (${RCLONE_REMOTE})..."
    rclone copy "${ZIPPED_BACKUP}" "${RCLONE_REMOTE}"
    echo "[$(date)] 🎉 Upload completed successfully!"

    # 3. Clean up remote backups older than 30 days
    echo "[$(date)] 🧹 Cleaning up remote backups older than 30 days..."
    rclone delete --min-age 30d "${RCLONE_REMOTE}" || true
else
    echo "[$(date)] ⚠️ 'rclone' is not installed or configured yet."
    echo "[$(date)] 💡 Please run 'rclone config' to set up your Google Drive remote."
fi

# 4. Clean up local backups older than 7 days
echo "[$(date)] 🧹 Cleaning local backups older than 7 days..."
find "${BACKUP_DIR}" -type f -name "portfolio_backup_*.gz" -mtime +7 -delete

echo "[$(date)] ✨ Database backup completed!"
