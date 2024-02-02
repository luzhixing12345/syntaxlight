
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
{
    "definitions": {
        "Schema1": {
            "not": {
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
