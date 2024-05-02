# syntaxlight

> 本项目仍在开发中, 尚不可用...

syntaxlight 是一个基于 BNF 的语法高亮的 python 库, 您可以 [在线浏览](https://luzhixing12345.github.io/syntaxlight/articles/全部文法高亮/C/) 文法高亮结果

目前支持 C/Python 等主流编程语言和 json xml 等主流标记语言的文法解析, 支持多种高亮主题以及自定义颜色(默认使用 Vscode 风格), 您可在此查看[全部文法支持和高亮支持](https://luzhixing12345.github.io/syntaxlight/articles/%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C/%E5%85%A8%E9%83%A8%E6%96%87%E6%B3%95%E6%94%AF%E6%8C%81/)

## 安装

```bash
pip install syntaxlight
```

## 快速开始

syntaxlight 提供了一个简易的 API 用于预览结果: `syntaxlight.example_display`

```python
import syntaxlight

syntaxlight.example_display('./1.c')

# syntaxlight.example_display('./your-code.c', style='one-dark-pro')
```

运行可以得到 `syntaxlight_example/` 文件夹, 使用浏览器打开其中的 index.html 即可预览. 同时会生成解析得到的抽象语法树 ast.dot, Vscode 用户可以下载 [graphviz-interactive-preview](https://marketplace.visualstudio.com/items?itemName=tintinweb.graphviz-interactive-preview) 插件预览, 或者安装 [graphviz](https://graphviz.org/) 之后使用下面的命令导出 png

```bash
dot -Tpng ./ast.dot -o ast.png
```

## 文档和 API

关于详细的 API 使用方法, 以及对于默认配置的修改情况请参阅 [syntaxlight 使用文档](https://luzhixing12345.github.io/syntaxlight/)

## 开发功能

本仓库的 Makefile 与 test.py 提供了对于测试用例的渲染预览, 运行后打开 syntaxlight_example/index.html 即可

```bash
# 浏览所有 C 测试用例集合渲染结果
make 

# 浏览所有 json 测试用例集合渲染结果
make t=json

# 浏览 json 第一个 test/json/1.json 测试用例渲染结果
make t=json i=1

# 浏览 toml 第一个 test/toml/1.json 测试用例在 one-dark-pro 风格下的渲染结果
make t=toml i=1 s=one-dark-pro
```

[now carbon](https://carbon.now.sh/) [ruslanspivak lsbasi-part1](https://ruslanspivak.com/lsbasi-part1/)

https://ruslanspivak.com/lsbasi-part1/ 

https://ruslanspivak.com/lsbasi-part1/

## 参考

- [Let's Build A Simple Interpreter](https://ruslanspivak.com/lsbasi-part1/)
- [tree-sitter](https://github.com/tree-sitter/tree-sitter)
- [pygments](https://pygments.org/)
- [carbon](https://carbon.now.sh/)
