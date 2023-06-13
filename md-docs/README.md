# syntaxlight

欢迎使用 syntaxlight!

syntaxlight 是一个基于 EBNF 的语法高亮的 python 库, 通常用于配合 Markdown 解析器完成网页 html 中 `<pre><code>` 标签内的代码高亮, 目前支持 C Python Lua 等常见编程语言和 json xml 等文件格式的文法解析

本文档使用 [zood](https://github.com/luzhixing12345/zood) 构建, 其 Markdown 解析器 [MarkdownParser](https://github.com/luzhixing12345/MarkdownParser) 即使用 syntaxlight 完成语法高亮, 您可在 [全部文法支持]() 中快速浏览所有高亮结果

## 文档结构

本文档分为两部分

- 用户手册

  这部分主要介绍如何使用 syntaxlight API 以及如何支持自定义 EBNF 规则匹配文本, 以及自定义高亮颜色

- 开发文档