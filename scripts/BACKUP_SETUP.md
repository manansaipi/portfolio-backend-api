# 🗄️ Automated Google Drive Database Backup Setup Guide

This guide explains how to automatically back up your backend database to **Google Drive** using `rclone` and a Linux `cron` scheduler.

---

## 🛠️ Step 1: Install `rclone`

Run the following command on your Linux server:

```bash
sudo apt update && sudo apt install -y rclone
```

*(Alternatively, use `curl https://rclone.org/install.sh | sudo bash`)*

---

## 🔑 Step 2: Configure Google Drive Remote

Run the interactive `rclone` configuration tool:

```bash
rclone config
```

Follow the prompts:
1. Type `n` for **New remote**.
2. Name it: **`gdrive`** (lowercase).
3. Storage type: Scroll or type `drive` (Google Drive).
4. Leave `client_id` and `client_secret` blank (press **Enter** for defaults).
5. Access Scope: Choose `1` (**Full access**).
6. Root Folder ID / Service Accountfile: Press **Enter** for defaults.
7. Advanced Config: Choose `n` (**No**).
8. Auto config / Browser login: Choose `y` (**Yes**) to authenticate with your Google account via browser.
9. Confirm configuration: Choose `y` (**Yes**), then `q` to quit.

---

## 🚀 Step 3: Test the Backup Script Manually

Run the backup script directly from the `backend/` folder:

```bash
./scripts/backup_to_gdrive.sh
```

You should see output like:
```text
[Sun Aug  2 01:20:00 2026] 📦 Starting database backup process...
[Sun Aug  2 01:20:00 2026] ⚙️ Backing up SQLite database...
[Sun Aug  2 01:20:01 2026] ✅ Created compressed backup: /path/to/portfolio_backup_20260802_012000.db.gz
[Sun Aug  2 01:20:01 2026] 🚀 Uploading to Google Drive (gdrive:Portfolio_Backups)...
[Sun Aug  2 01:20:03 2026] 🎉 Upload completed successfully!
```

Check your **Google Drive** — you will find a new folder named `Portfolio_Backups` containing your compressed database backup!

---

## ⏰ Step 4: Schedule Daily Automated Backups (Cron Job)

To run the backup automatically every day at **2:00 AM**:

1. Open your crontab editor:
   ```bash
   crontab -e
   ```

2. Add the following line at the end (update `/path/to/your/backend` with your actual server path):
   ```cron
   0 2 * * * /bin/bash /path/to/your/backend/scripts/backup_to_gdrive.sh >> /path/to/your/backend/database_backup/backup.log 2>&1
   ```

3. Save and exit.

---

## 🧹 Automatic Cleanup Policies Included

- **Local backups:** Automatically deletes files older than **7 days** to save server disk space.
- **Google Drive backups:** Automatically deletes files older than **30 days** to manage cloud storage.
