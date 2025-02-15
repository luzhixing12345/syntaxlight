
# API

欢迎使用 syntaxlight, syntaxlight 是一个用于解析代码并生成 html 字符串的 python 库, 可以用于配合 Markdown 解析器完成网页 html 中 `<pre><code>` 标签内的代码高亮

```bash
pip install syntaxlight
```

## 解析代码

syntaxlight 提供了两个常用的 API 用于解析代码, 分别用于解析源代码字符串和从文件中解析代码, 其中语言类型(language)可选, 如果不指定则根据文件后缀名自动判断

```python
def parse(text: str, language=None, file_path=None) -> ParseResult:
    ...

def parse_file(file_path: str, language=None) -> ParseResult:
    ...
```

返回值 ParseResult 是一个包含解析结果的类, 其包含三部分内容:

```python
class ParseResult:
    success: bool  # 是否解析成功
    parser: Parser  # 解析器
    error: Error  # 错误信息(如果有)
```

其中 success 表示解析是否成功, parser 是一个包含解析结果的类, error 是一个包含错误信息的类, 如果没有错误则为 None.

对于代码语法正确的情况下 success 为 True, 此时可以直接通过 parser.to_html() 得到 html 字符串, 如果代码语法错误则 success 为 False, 此时 error 包含了错误信息, 可以直接打印 print(error) 查看错误位置, 默认错误输出格式如下所示

![20250215200739](https://raw.githubusercontent.com/learner-lu/picbed/master/20250215200739.png)

syntaxlight 会尽力进行解析, 即使出现错误也会以默认的关键字匹配的方式将所有代码段完成解析, 因此即使代码语法错误, 也可以得到一个较为完整的解析结果, 即无论 success 为 True/False, parser.to_html() 始终会返回解析结果的字符串

> 考虑错误处理的一个完整的示例写法如下所示

```python
import syntaxlight

result = syntaxlight.parse_file("a.c")
if not result.success:
    print(result.error)
print(result.parser.to_html())
```

```python
import syntaxlight

code = """
#include <stdio.h>

int main() {
    printf("hello world!\n");
    return 0;
}
"""

result = syntaxlight.parse(code, 'C')
if not result.success:
    print(result.error)
print(result.parser.to_html())
```

## 导出 css

syntaxlight 通常用于配合 Markdown 解析器完成网页 html 中 `<pre><code>` 标签内的代码高亮, 因此为了正确高亮显示还需要导出 css 文件

syntaxlight 提供了一个 API 用于导出 css 文件, 其中 style 参数用于指定导出样式, 目前支持三种样式(vscode, one-dark-pro, monokai), 默认为 vscode

```python
def export_css(languages: List[str], export_dir: str = ".", style: str = "vscode"):
    ...
```

> 当然您也可以自定义高亮颜色, 详见 [自定义高亮颜色](./自定义颜色.md)

假设我们希望导出 c, python, lua 三种语言的 css 文件到 css 目录下, 可以使用如下代码

```python
import syntaxlight

syntaxlight.export_css(['c','python','lua'], export_dir='./css')
# <link rel='stylesheet' href=./css/c.css />
# <link rel='stylesheet' href=./css/python.css />
# <link rel='stylesheet' href=./css/lua.css />
```

最后将 css 文件路径引入你的 html 即可

## 支持语言

当前版本的 syntaxlight 支持的语言类型有限, 可以参阅 [全部文法支持](./全部文法支持.md)

您可以使用如下 api 查看当前版本 syntaxlight 支持的语言类型以及是否支持您期望的语言类型

```python
import syntaxlight

# 查看当前版本 syntaxlight 支持的语言类型
print(syntaxlight.supported_languages)

if syntaxlight.is_lanaguage_support('c'):
    print("c is supported")
else:
    print("c is not supported")
```

## 网页预览

syntaxlight 提供了一个简易的 API 用于预览结果: `syntaxlight.example_display`

```python
import syntaxlight

syntaxlight.example_display('./test/c/2.c')

# syntaxlight.example_display('./your-code.c', style='one-dark-pro')
```

运行可以得到 `syntaxlight_example/` 文件夹, 使用浏览器打开其中的 index.html 即可预览

## 高级用法

### 高亮 line/token

如果您希望对代码中的某一行或者某个 token 进行高亮强调, 例如

```c{4}
#include <stdio.h>

int main() {
    printf("hello world!\n");
    return 0;
}
```

只需要在 parse.to_html() 中传入两个变量即可

```python
import syntaxlight

result = syntaxlight.parse_file("a.c")
if not result.success:
    print(result.error)

print(result.parser.to_html(hightlight_lines = [4])) # 高亮第四行
```

### ast

同时会生成解析得到的抽象语法树 ast.dot, Vscode 用户可以下载 [graphviz-interactive-preview](https://marketplace.visualstudio.com/items?itemName=tintinweb.graphviz-interactive-preview) 插件预览, 或者安装 [graphviz](https://graphviz.org/) 之后使用下面的命令导出 png

```bash
dot -Tpng ./ast.dot -o ast.png
```