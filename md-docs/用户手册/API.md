
# API

## 网页预览

syntaxlight 提供了一个简易的 API 用于预览结果: `syntaxlight.example_display`

```python
import syntaxlight

syntaxlight.example_display('./test/c/2.c')

# syntaxlight.example_display('./your-code.c', style='one-dark-pro')
```

运行可以得到 `syntaxlight_example/` 文件夹, 使用浏览器打开其中的 index.html 即可预览

## API

> 本项目仍在开发中, API 尚未确定

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
