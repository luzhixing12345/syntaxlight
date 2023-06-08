

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

syntaxlight.export_css(['c','python','lua'], export_name='index.css')
# 保存得到 index.css 文件, 将其引入 html 即可: <link rel='stylesheet' href=./index.css />
