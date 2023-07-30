
# json
## [1.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/1.json)

```json
{
    "definitions": {
        "Schema1": {
            "not": {
                "$ref": "#/definitions/Schema1"
            }
        }
    },
    "$ref": "#/definitions/Schema1",
    "23": -12310e10,
    "123": true,
    "123456": false,
    "1999": null
}
```
## [2.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/2.json)

```json
{
    "name": "John",
    "age": 30e+10,
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY"
    }
}
```
## [3.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/3.json)

```json
[
    "apple",
    "banana",
    "orange"
]
```
## [4.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/4.json)

```json
[{
    "students": [
        {
            "name": "John",
            "age": 20
        },
        {
            "name": "Jane",
            "age": 22
        }
    ]
}]
```
## [5.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/5.json)

```json
{
    "name": "John",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY"
    },
    "spouse": {
        "$ref": "#/friends/0"
    },
    "friends": [
        {
            "name": "Jane",
            "age": 28,
            "abc": {
                "name": "Tom",
                "age": 32
            }
        },
        {
            "name": "Tom",
            "age": 32
        }
    ]
}
```
## [6.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/6.json)

```json
[
    {
        "id": 1,
        "first_name": "Jeanette",
        "last_name": "Penddreth",
        "email": "jpenddreth0@census.gov",
        "gender": "Female",
        "ip_address": "26.58.193.2"
    },
    {
        "id": 2,
        "first_name": "Giavani",
        "last_name": "Frediani",
        "email": "gfrediani1@senate.gov",
        "gender": "Male",
        "ip_address": "229.179.4.212"
    },
    {
        "id": 3,
        "first_name": "Noell",
        "last_name": "Bea",
        "email": "nbea2@imageshack.us",
        "gender": "Female",
        "ip_address": "180.66.162.255"
    },
    {
        "id": 4,
        "first_name": "Willard",
        "last_name": "Valek",
        "email": "wvalek3@vk.com",
        "gender": "Male",
        "ip_address": "67.76.188.26"
    }
]
```
## [7.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/7.json)

```json
{
    "employees": [
        {
            "firstName": "John",
            "lastName": "Doe",
            "skills": [
                "Python",
                "Java",
                "SQL"
            ],
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY"
            }
        },
        {
            "firstName": "Jane",
            "lastName": "Smith",
            "skills": [
                "C++",
                "JavaScript"
            ],
            "address": {
                "street": "456 Elm St",
                "city": "San Francisco",
                "state": "CA",
                "123": 123
            }
        }
    ]
}
```
## [8.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/8.json)

```json
[
    "阿加莎尽快",
    "阿斯顿杰拉德",
    "爱神的箭卡的很",

```
## [9.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/9.json)

```json
123
```
## [10.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/10.json)

```json
{
    "definitions": {
        "Schema1": {
            "not": {
                "$ref": "#/definitions/Schema1",
            }
        }
    },
    "$ref": "#/definitions/Schema1",
    "23": -12310,
    "123": true,
    "123456": false,
    "1999": null
}
```
## [11.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/11.json)

```json
{
    "definitions": {
        "Schema1": {
            "not": {
                "$ref": "#/definitions/Schema1"
                "$ref": "#/definitions/Schema1"
            }
        }
    },
    "$ref": "#/definitions/Schema1",
    "23": -12310,
    "123": true,
    "123456": false,
    "1999": null
}
```
## [12.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/12.json)

```json
[
    "apple",
    "banana",
    "orange"
    "orange"
]
```
## [13.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/13.json)

```json
[
    "apple",
    "banana",
    "orange",
]
```
## [14.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/14.json)

```json
[
    "apple",
    "banana",
    "orange",
    {
        "123": -abc
    }
]
```
## [15.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/15.json)

```json
[
    "apple",
    "banana",
    "orange"
]
123
```
## [16.json](https://github.com/luzhixing12345/syntaxlight/tree/main/test/json/16.json)

```json
{
    "clangd.fallbackFlags": [
        "-I${workspaceFolder}/include"
    ],
    "clangd.arguments": [
        "--background-index", // 在后台自动分析文件(基于complie_commands)
        "-j=12", // 同时开启的任务数量
        "--clang-tidy", // clang-tidy功能
        "--clang-tidy-checks=performance-*,bugprone-*",
        "--all-scopes-completion", // 全局补全(会自动补充头文件)
        "--completion-style=detailed", // 更详细的补全内容
        "--header-insertion=iwyu" // 补充头文件的形式
    ]
}
```
