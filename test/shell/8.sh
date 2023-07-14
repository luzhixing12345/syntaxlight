#!/bin/bash

# 读取用户输入
read -p "Enter your name: " name
echo "Hello, $name!"

# 将命令输出重定向到文件
ls -l > file_list.txt

# 从文件中读取输入并进行处理
while read line; do
  echo "Line: $line"
done < input_file.txt
