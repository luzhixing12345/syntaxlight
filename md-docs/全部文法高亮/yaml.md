
# yaml
## [1.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/1.yml)

```yaml
server:
  port: 8080
  hostname: example.com

database:
  host: db.example.com
  port: 3306
  username: user
  password: pass
  dbname: mydb

```
## [2.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/2.yml)

```yaml
vars:
   service1:
       config: &service_config
           env: prod
           retries: 3
           version: 4.8
   service2:
       config: *service_config
   service3:
       config: *service_config
```
## [3.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/3.yml)

```yaml
---
# A sample yaml file
company: spacelift
domain:
 - devops
 - devsecops
tutorial:
  - yaml:
      name: "YAML Ain't Markup Language"
      type: awesome
      born: 2001
  - json:
      name: JavaScript Object Notation
      type: great
      born: 2001
  - xml:
      name: Extensible Markup Language
      type: good
      born: 1996
author: omkarbirade
published: true

```
## [4.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/4.yml)

```yaml
name: CI/CD
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout Repo
      uses: actions/checkout@v2
    - name: Build and Test
      run: |
        npm install
        npm run build
    - name: Deploy
      uses: some/deployment-action@v1
      with:
        server: production
        token: ${{ secrets.DEPLOY_TOKEN }}

```
## [5.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/5.yml)

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get a list of users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              example:
                - id: 1
                  name: John
                - id: 2
                  name: Jane

```
## [6.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/6.yml)

```yaml
apiVersion: v2
name: myapp
description: A Helm chart for my app
version: 0.1.0
dependencies:
  - name: redis
    version: 6.0.0
    repository: https://charts.bitnami.com/bitnami
values:
  replicaCount: 3
  image:
    repository: myapp
    tag: latest
  resources:
    limits:
      cpu: 1
      memory: 512Mi

```
## [7.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/7.yml)

```yaml
---
# A sample yaml file
company: !!str spacelift
domain:
 - !!str devops
 - !!str devsecops
tutorial:
   - name: !!str yaml
   - type: !!str awesome
   - rank: !!int 1
   - born: !!int 2001
author: !!str omkarbirade
published: !!bool true
```
## [8.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/8.yml)

```yaml
# 文档1:标量和键值对
string_example: "This is a string"
number_example: 42
boolean_example: true

object_example:
  key1: value1
  key2: value2

# 文档2:列表和嵌套结构
list_example:
  - item1
  - item2
  - sub_list:
      - sub_item1
      - sub_item2

# 文档3:锚点和别名
anchor_example: &example_anchor
  key1: value1
  key2: value2

alias_example: *example_anchor

# 文档4:多行字符串和折叠块
multiline_string: |
  This is a multiline
  string with preserved line breaks.

folded_block: >
  This is a folded block
  with folded line breaks.

# 文档5:标签和属性
tagged_example: !!str "This is a tagged string"

property_example: &property_anchor
  <<: *example_anchor
  property: value

# 文档6:流式序列和流式映射
flow_sequence: [item1, item2, item3]
flow_mapping: {key1: value1, key2: value2}

# 文档7:引用、换行注释和块注释
reference_example: *property_anchor

key_with_comment: value  # 这是一个行内注释

block_comment: |
  This is a block comment
  spanning multiple lines.

# 文档8:特殊符号和转义字符
special_symbols: ':-{},[]?*&!|#<>%@`'

escaped_characters: "This string contains\nnewlines and\ttabs."

# 文档9:时间戳和空值
timestamp_example: 2023-08-21T12:34:56Z
null_example: null

# 文档10:嵌套文档
nested_document:
  sub_document:
    key1: value1
    key2: value2

...
# 可以继续添加更多文档

```
## [9.yml](https://github.com/luzhixing12345/syntaxlight/tree/main/test/yaml/9.yml)

```yaml
name: Test with Coverage

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install coverage

    - name: Run tests with coverage
      run: |
        coverage run -m unittest
        coverage xml -i
      env:
        COVERAGE_RUN: True

    - name: Upload coverage report to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```
