#!/bin/bash

LOG_FILE="/var/log/app.log"
MAX_SIZE=1000000
BACKUP_COUNT=5

# 检查日志文件大小
log_size=$(wc -c < "$LOG_FILE")
if [[ $log_size -gt $MAX_SIZE ]]; then
  # 备份旧的日志文件
  for ((i=$BACKUP_COUNT; i>1; i--)); do
    prev=$((i-1))
    mv "$LOG_FILE.$prev" "$LOG_FILE.$i" 2>/dev/null
  done
  mv "$LOG_FILE" "$LOG_FILE.1"

  # 创建新的日志文件
  touch "$LOG_FILE"
fi

# 写入日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log entry" >> "$LOG_FILE"
