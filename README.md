# syntaxlight

> 本项目仍在开发中, 尚不可用...

syntaxlight 是一个基于 BNF 的语法高亮的 python 库, 您可以 [在线浏览]() 文法高亮结果

目前支持 C/Python 等主流编程语言和 json xml 等主流标记语言的文法解析, 支持多种高亮主题以及自定义颜色(默认使用 Vscode 风格), 您可在此查看[全部文法支持和高亮支持](https://luzhixing12345.github.io/syntaxlight/articles/%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C/%E5%85%A8%E9%83%A8%E6%96%87%E6%B3%95%E6%94%AF%E6%8C%81/)

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

为了方便用户使用, syntaxlight 提供了一个简易的示例用于预览结果和调整

```python
import syntaxlight

syntaxlight.example_display()
```

运行可以得到一个 `syntaxlight_example/` 文件夹, 使用浏览器打开其中的 index.html 可以快速预览 文法高亮结果 以及 切换不同高亮风格, 并提供了一键导出的快捷选项

## 文档和 API

[syntaxlight 使用文档](https://luzhixing12345.github.io/syntaxlight/)

文档中提供了比较详细的 API 使用方法, 以及对于默认配置的修改情况

## 参考

- [Let's Build A Simple Interpreter](https://ruslanspivak.com/lsbasi-part1/)
- [pygments](https://pygments.org/)
- [carbon](https://carbon.now.sh/)