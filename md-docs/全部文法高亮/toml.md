
# toml
## [1.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/1.toml)

```toml
# This is a TOML document

title = "TOML Example"
title1adb =  100

[owner]
name = "Tom Preston-Werner"
dob = 1979-05-27T07:32:00-08:00

[database]
enabled = true
ports = [ 8000, 8001, 8002 ]
data = [ ["delta", "phi"], [3.14] ]
temp_targets = { cpu = 79.5, case = 72.0 }

[servers]

[servers.alpha]
ip = "10.0.0.1"
role = "frontend"

[servers.beta]
ip = "10.0.0.2"
role = "backend"
```
## [2.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/2.toml)

```toml
[[fruits]]
name = "apple"

abc = [1,2,]

[fruits.physical]  # 子表
color = "red"
shape = "round"

[[fruits.varieties]]  # 嵌套表数组
name = "red delicious"

[[fruits.varieties]]
name = "granny smith"

[[fruits]]
name = "banana"

[[fruits.varieties]]
name = "plantain"
```
## [3.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/3.toml)

```toml
# 字符串
str1 = "Hello, world!"
str2 = 'Hello, "world"!'
str3 = 'Hello, \'world\'!'

# 数字
int1 = 42
int2 = +42
int3 = -42
float1 = 3.14
float2 = +3.14
float3 = -3.14

# 布尔值
bool1 = true
bool2 = false

# 日期和时间
date1 = 2023-06-16
time1 = 13:30:00
datetime1 = 2023-06-16T13:30:00Z

# 小数
flt1 = +1.0
flt2 = 3.1415
flt3 = -0.01

# 指数
flt4 = 5e+22
flt5 = 1e06
flt6 = -2E-2

# 都有
flt7 = 6.626e-34
```
## [4.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/4.toml)

```toml
# 数组
arr1 = [1, 2, 3]
arr2 = [
    "apple",
    "banana",
    "cherry"
]
arr3 = [
    { name = "Alice", age = 30 },
    { name = "Bob", age = 40 }
]

# 嵌套数组
arr4 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# 表
[person1]
name = "Alice"
age = 30

[person2]
name = "Bob"
age = 40

# 嵌套表
[person3]
name = "Charlie"
age = 50

[person3.address]
city = "New York"
state = "NY"
```
## [5.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/5.toml)

```toml
# 这是一条注释

# 这个表有一个字符串字段和一个整数字段
[table1]
string_field = "Hello, world!"  # 字符串字段
int_field = 42  # 整数字段

# 这是一条空白行

# 第二个元素是一个整数


# 第三个元素是一个表
[arr1.table1]
name = "Alice"
age = 30
# 123
```
## [6.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/6.toml)

```toml
[tool.poetry]
name = "syntaxlight"
version = "0.0.1"
description = "syntax highlight based on EBNF"
authors = ["luzhixing12345 <luzhixing12345@163.com>"]
license = "MIT"
readme = "README.md"
repository = "https://github.com/luzhixing12345/syntaxlight"
documentation = "https://luzhixing12345.github.io/syntaxlight/"

[tool.poetry.dependencies]
python = "^3.10"


[build-system-123]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

```
## [7.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/7.toml)

```toml
# 这是一个全行注释
key = "value"  # 这是一个行末注释
another = "# 这不是一个注释"

"127.0.0.1" = "value"
"character encoding" = "value"
"ʎǝʞ" = "value"
'key2' = "value"
'quoted "value"' = "value"


"" = "blank"     # 合法但不鼓励
'' = 'blank'     # 合法但不鼓励

name = "Orange"
physical.color = "orange"
physical.shape = "round"
site."google.com" = true

fruit.name = "banana"     # 这是最佳实践
fruit. color = "yellow"    # 等同于 fruit.color
fruit . flavor = "banana"   # 等同于 fruit.flavor

str1 = """
Roses are red
Violets are blue"""

str4 = """这有两个引号:"".够简单."""
# str5 = """这有三个引号:"""."""  # 非法
str5 = """这有三个引号:""\"."""
str6 = """这有十五个引号:""\"""\"""\"""\"""\"."""

# "这,"她说,"只是个无意义的条款."
str7 = """这,"她说,"只是个无意义的条款."""

winpath  = 'C:\Users\nodejs\templates'
winpath2 = '\\ServerX\admin$\system32' # 这里有点小问题
quoted   = 'Tom "Dubs" Preston-Werner'
regex    = '<\i\c*\s*>'

regex2 = '''I [dw]on't need \d{2} apples'''
lines  = '''
原始字符串中的
第一个换行被剔除了.
   所有其它空白
   都保留了.
'''

quot15 = '''这有十五个引号:"""""""""""""""'''

# apos15 = '''这有十五个撇号:''''''''''''''''''  # 非法
apos15 = "这有十五个撇号:'''''''''''''''"

# '那,'她说,'仍然没有意义.'
str = ''''那,'她说,'仍然没有意义.'''

```
## [8.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/8.toml)

```toml

["123"]
a = 10
b = 10
c = 10
d = 10
1
```
## [9.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/9.toml)

```toml

a.+100 = 100
```
## [10.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/10.toml)

```toml

a = ooo
```
## [11.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/11.toml)

```toml

a = -qqq
```
## [12.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/12.toml)

```toml

a = [1 2 3]
```
## [13.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/13.toml)

```toml

a = {a=100 b=100 3}
```
## [14.toml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/toml/14.toml)

```toml
[[fruits.varieties]]  # 嵌套表数组
name = "red delicious"

[[fruits.varieties]]
name = "granny smith"

[[fruits]]
name = "banana"

[[fruits.varieties]]
name = "plantain" name = "plantain" name = "plantain"
```
