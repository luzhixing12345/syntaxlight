
import os
import re
from typing import Dict, List, Union

def export_css(languages: List[str], export_name: str = "index.css", style: str = "vscode"):

    style = 'one-dark-pro'
    style = 'monokai'
    
    themes = read_buildin_css()
    if style in themes:
        theme = themes[style]
        syntaxlight_path = os.path.dirname(__file__)
        for language in languages:
            origin_css_file = os.path.join(syntaxlight_path, 'css', f'{language}.css')
            if not os.path.exists(origin_css_file):
                print(f'no {language} css file')
                exit(1)
            with open(origin_css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            # 使用主题颜色替换 css 文件中的对应类型
            for type_name, color in theme.items():
                css_content = css_content.replace(type_name, color)
            
            with open(export_name , 'w', encoding='utf-8') as f:
                f.write(css_content)
    else:
        print(f"style {style} is not a builtin style")
        exit(1)


def read_buildin_css() -> Dict[str, Dict[str, str]]:
    '''
    获取 css/all.css 中所有内置主题颜色, 匹配方式比较粗糙, 采用正则, 记得格式化
    '''
    syntaxlight_path = os.path.dirname(__file__)
    all_css_file_path = os.path.join(syntaxlight_path, 'css', 'all.css')
    
    with open(all_css_file_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    pattern = re.compile(r'\.(.*?) \{(.*?)\}', re.DOTALL)
    matches = re.findall(pattern, css_content)
    themes:Dict[str, Dict[str, str]] = {}
    for result in matches:
        _css_colors = re.findall(r'color: (.*?); /\* @(.*?) ', result[1])
        css_colors = {}
        for css_color in _css_colors:
            css_colors[css_color[1]] = css_color[0]
        themes[result[0]] = css_colors
    return themes

    