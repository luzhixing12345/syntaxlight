#!/bin/bash

SOURCE_DIR="/path/to/source"
BACKUP_DIR="/path/to/backup"
DATE=$(date '+%Y%m%d')

# 创建备份目录
mkdir -p "$BACKUP_DIR/$DATE"

# 复制源目录的内容到备份目录
cp -R "$SOURCE_DIR" "$BACKUP_DIR/$DATE"

echo "Backup of $SOURCE_DIR created in $BACKUP_DIR/$DATE"
