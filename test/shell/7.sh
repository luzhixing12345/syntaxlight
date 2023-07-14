#!/bin/bash

# 定义函数
welcome() {
  echo "Welcome, $1!"
}

# 调用函数
welcome "John"

# 执行外部命令并获取结果
result=$(ls -l)
echo "$result"

# 调用外部脚本并传递参数
./external_script.sh arg1 arg2
