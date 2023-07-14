#!/bin/bash

# 定义变量
count=0

# 循环执行命令并进行条件判断
while [[ $count -lt 10 ]]; do
  echo "Count: $count"
  if [[ $count -eq 5 ]]; then
    echo "Reached 5, breaking the loop"
    break
  fi
  count=$((count+1))
done

# 列出目录下的文件并进行条件判断
for file in *; do
  if [[ -f $file ]]; then
    echo "File: $file"
  elif [[ -d $file ]]; then
    echo "Directory: $file"
  fi
done
