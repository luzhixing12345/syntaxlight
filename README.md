# syntaxlight

syntaxlight 是一个基于 EBNF 的语法高亮的 python 库, 您可以 [在线浏览]() 所有文法的高亮结果

目前支持 C Python Lua 等常见编程语言和 json xml 等文件格式的文法解析, 默认使用 Vscode 风格的高亮显示

除此之外也支持自定义 EBNF 规则匹配文本, 以及自定义高亮颜色

## 安装

```bash
pip install syntaxlight
```

## 快速开始

```python
import syntaxlight

code = """
#include <stdio.h>

int main() {
    printf("hello world!\n");
    return 0;
}
"""

html = syntaxlight.parse(code, 'C')
print(html)
```

syntaxlight 通常用于配合 Markdown 解析器完成网页 html 中 `<pre><code>` 标签内的代码高亮, 因此为了正确高亮显示还需要导出 css 文件

```python
import syntaxlight

syntaxlight.export_css(['c','python','lua'], export_name='index.css')
# 保存得到 index.css 文件, 将其引入 html 即可: <link rel='stylesheet' href=./index.css />
```

除此之外为了方便用户使用, syntaxlight 提供了一个简易的示例用于预览结果和调整

```python
import syntaxlight

syntaxlight.example_display()
```

运行可以得到一个 `syntaxlight_example/` 文件夹, 使用浏览器打开其中的 index.html 可以快速预览 文法高亮结果 以及 切换不同高亮风格, 并提供了一键导出的快捷选项

## 文档和 API

[syntaxlight 使用文档](https://luzhixing12345.github.io/syntaxlight/)

文档中提供了比较详细的 API 使用方法, 以及对于默认配置的修改情况

## 参考

- [pygments](https://pygments.org/)