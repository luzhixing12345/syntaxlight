# syntaxlight

> 本项目仍在开发中, 尚不可用...

syntaxlight 是一个基于 BNF 的语法高亮的 python 库, 您可以 [在线浏览]() 文法高亮结果

目前支持 C/Python 等主流编程语言和 json xml 等主流标记语言的文法解析, 支持多种高亮主题以及自定义颜色(默认使用 Vscode 风格), 您可在此查看[全部文法支持和高亮支持](https://luzhixing12345.github.io/syntaxlight/articles/%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C/%E5%85%A8%E9%83%A8%E6%96%87%E6%B3%95%E6%94%AF%E6%8C%81/)

## 安装

```bash
pip install syntaxlight
```

## 快速开始

syntaxlight 提供了一个简易的 API 用于预览结果: `syntaxlight.example_display`

```python
import syntaxlight

syntaxlight.example_display('./test/c/2.c')

# syntaxlight.example_display('./your-code.c', style='one-dark-pro')
```

运行可以得到 `syntaxlight_example/` 文件夹, 使用浏览器打开其中的 index.html 即可预览

## 文档和 API

关于详细的 API 使用方法, 以及对于默认配置的修改情况请参阅 [syntaxlight 使用文档](https://luzhixing12345.github.io/syntaxlight/)

## 参考

- [Let's Build A Simple Interpreter](https://ruslanspivak.com/lsbasi-part1/)
- [pygments](https://pygments.org/)
- [carbon](https://carbon.now.sh/)