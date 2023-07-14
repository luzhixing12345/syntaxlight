#!/bin/bash

# 定义任务函数
task() {
  echo "Starting task $1"
  sleep $1
  echo "Task $1 completed"
}

# 并发执行任务
for i in {1..5}; do
  task $i &
done

# 等待所有任务完成
wait

echo "All tasks completed"
