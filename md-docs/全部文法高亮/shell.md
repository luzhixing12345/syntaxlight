
# shell
## [1.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/1.sh)

```shell
sudo apt install build-essential git m4 scons zlib1g zlib1g-dev \
    libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev \
    python3-dev python-is-python3 libboost-all-dev pkg-config libhdf5-dev libpng-dev
```
## [2.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/2.sh)

```shell
#!/bin/bash
# Simple script to list version numbers of critical development tools
export LC_ALL=C
bash --version | head -n1 | cut -d" " -f2-4
MYSH=$(readlink -f /bin/sh)
echo "/bin/sh -> $MYSH"
echo $MYSH | grep -q bash || echo "ERROR: /bin/sh does not point to bash"
unset MYSH
echo -n "Binutils: "; ld --version | head -n1 | cut -d" " -f3-
bison --version | head -n1
if [ -h /usr/bin/yacc ]; then
 echo "/usr/bin/yacc -> `readlink -f /usr/bin/yacc`";
elif [ -x /usr/bin/yacc ]; then
 echo yacc is `/usr/bin/yacc --version | head -n1`
else
 echo "yacc not found"
fi
echo -n "Coreutils: "; chown --version | head -n1 | cut -d")" -f2
diff --version | head -n1
find --version | head -n1
gawk --version | head -n1
if [ -h /usr/bin/awk ]; then
 echo "/usr/bin/awk -> `readlink -f /usr/bin/awk`";
elif [ -x /usr/bin/awk ]; then
 echo awk is `/usr/bin/awk --version | head -n1`
else
 echo "awk not found"
fi
gcc --version | head -n1
g++ --version | head -n1
grep --version | head -n1
gzip --version | head -n1
cat /proc/version
m4 --version | head -n1
make --version | head -n1
patch --version | head -n1
echo Perl `perl -V:version`
python3 --version
sed --version | head -n1
tar --version | head -n1
makeinfo --version | head -n1 # texinfo version
xz --version | head -n1
echo 'int main(){}' > dummy.c && g++ -o dummy dummy.c
if [ -x dummy ]
 then echo "g++ compilation OK";
 else echo "g++ compilation failed"; fi
rm -f dummy.c dummy

```
## [3.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/3.sh)

```shell
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

```
## [4.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/4.sh)

```shell
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

```
## [5.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/5.sh)

```shell
#!/bin/bash

SOURCE_DIR="/path/to/source"
BACKUP_DIR="/path/to/backup"
DATE=$(date '+%Y%m%d')

# 创建备份目录
mkdir -p "$BACKUP_DIR/$DATE"

# 复制源目录的内容到备份目录
cp -R "$SOURCE_DIR" "$BACKUP_DIR/$DATE"

echo "Backup of $SOURCE_DIR created in $BACKUP_DIR/$DATE"

```
## [6.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/6.sh)

```shell
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

```
## [7.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/7.sh)

```shell
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

```
## [8.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/8.sh)

```shell
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

```
## [9.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/9.sh)

```shell
$ zood
zood使用方法见 https://luzhixing12345.github.io/zood/

  zood init         初始化仓库
  zood new A B      创建A目录下的B文件
  zood new A        创建根目录下的A文件
  zood update       更新dir.yml顺序
  zood -g           生成docs/目录
  zood clean        删除docs/目录
  zood config       获取配置文件
  zood -s           更新配置文件
其他:
  zood poetry <choice>   更新PYPI库版本
             choice = None(default) 发布版本更新
             choice = sub           次版本更新
             choice = main          主版本更新
  zood vsce <choice>     更新Vscode扩展版本
             choice = None(default) 发布版本更新
             choice = sub           次版本更新
             choice = main          主版本更新


sudo apt install build-essential git m4 scons zlib1g zlib1g-dev \
    libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev \
    python3-dev python-is-python3 libboost-all-dev pkg-config libhdf5-dev libpng-dev

git clone https://gem5.googlesource.com/public/gem5

cd gem5
scons build/X86/gem5.opt -j 4
```
## [10.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/10.sh)

```shell
Error: Can't find a suitable python-config, tried ['python3-config','python-config']
Error: Can't find a working Python installation

python3 `which scons` build/X86/gem5.opt

M4 macro processor not installed
Protobuf 3.12.3 problem
Wrong gcc version

alias gem5=/home/kamilu/gem5/build/X86/gem5.opt

pip install -r requirements.txt
sudo apt install pre-commit

sudo apt rmeove pre-commit
rm -r .git/hooks

pip install pydot
sudo apt install graphviz

dot -Tpng -o config.png config.dot
```
## [11.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/11.sh)

```shell
阿斯顿金克拉
└── traces
    ├── amptjp-bal.rep
    ├── binary-bal.rep
    ├── binary2-bal.rep
    ├── cccp-bal.rep
    ├── coalescing-bal.rep
    ├── cp-decl-bal.rep
    ├── expr-bal.rep
    ├── random-bal.rep
    ├── random2-bal.rep
    ├── realloc-bal.rep
    └── realloc2-bal.rep
```
## [12.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/12.sh)

```shell
root@kamilu:~# sudo apt install numactl

root@kamilu:~# numactl --hardware
available: 1 nodes (0)
node 0 cpus: 0
node 0 size: 914 MB
node 0 free: 148 MB
node distances:
node   0
  0:  10

(base) kamilu@LZX:~/csapplab$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
```
## [13.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/13.sh)

```shell
长选项与短选项等价

-A, --show-all           等价于"-vET"组合选项.
-b, --number-nonblank    只对非空行编号,从1开始编号,覆盖"-n"选项.
-e                       等价于"-vE"组合选项.
-E, --show-ends          在每行的结尾显示'$'字符.
-n, --number             对所有行编号,从1开始编号.
-s, --squeeze-blank      压缩连续的空行到一行.
-t                       等价于"-vT"组合选项.
-T, --show-tabs          使用"^I"表示TAB(制表符).
-u                       POSIX兼容性选项,无意义.
-v, --show-nonprinting   使用"^"和"M-"符号显示控制字符,除了LFD(line feed,即换行符'\n')和TAB(制表符).

--help                   显示帮助信息并退出.
--version                显示版本信息并退出.
```
## [14.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/14.sh)

```shell
$ ./re2postfix "a(abc|c|bc)+ab+"

[a]: token_number = [0] token_number = [1]
[(]: token_number = [1] pipe_number = [0] -> p++
[a]: token_number = [0] token_number = [1]
[b]: token_number = [1] token_number = [2]
[c]: token_number = [2] token_number = [2]
[|]: token_number = [2] pipe_number = [1]
[c]: token_number = [0] token_number = [1]
[|]: token_number = [1] pipe_number = [2]
[b]: token_number = [0] token_number = [1]
[c]: token_number = [1] token_number = [2]
[)]: token_number = [2] pipe_number = [2]
[+]:
[a]: token_number = [2] token_number = [2]
[b]: token_number = [2] token_number = [2]
[+]:

postfix = aab.c.cbc.||+.a.b+.
```
## [15.sh](https://github.com/luzhixing12345/syntaxlight/tree/main/test/shell/15.sh)

```shell
make GRADEFLAGS=find grade
# == Test xargs == xargs: OK (2.6s)
```
