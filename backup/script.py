#!/usr/bin/python3

import logging
import os
from datetime import datetime

# ================================================
# VARS
# ================================================

BACKUP_PATH = "/media/sda/volumes/filebrowser/"
DEST_BACKUPS_PATH = "/home/brian/backups/"
MAX_BACKUPS = 3

# ================================================
# CONFIGS
# ================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s (%(process)d) - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ================================================
# SCRIPT
# ================================================

if not os.path.exists(BACKUP_PATH) or not os.listdir(BACKUP_PATH):
    logging.error(f"BACKUP_PATH is empty or not exists")
    exit(1)

if not os.path.exists(DEST_BACKUPS_PATH):
    os.system(f"mkdir -p {DEST_BACKUPS_PATH}")

if len(os.listdir(DEST_BACKUPS_PATH)) >= MAX_BACKUPS:

    list_files_names = os.listdir(DEST_BACKUPS_PATH)
    list_files_names.sort()

    most_old_backup_file_name = list_files_names[0]
    os.system(
        f"rm -fr {os.path.join(DEST_BACKUPS_PATH, most_old_backup_file_name)}")

time_format = datetime.now().strftime("%Y_%m_%d+%H_%M_%S")
dest_backup_tar_name = f"{time_format}.tar.gz"

final_dest_backup_path = os.path.join(DEST_BACKUPS_PATH, dest_backup_tar_name)

os.system(
    f"tar -Pcpzf {final_dest_backup_path} {BACKUP_PATH}")
