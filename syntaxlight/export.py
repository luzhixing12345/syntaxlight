import os
from typing import Dict, List
import json


def export_css(languages: List[str], export_name: str = "index.css", style: str = "vscode"):
    syntaxlight_path = os.path.dirname(__file__)
    json_file_path = os.path.join(syntaxlight_path, "css", "themes.json")
    with open(json_file_path, "r", encoding="utf-8") as f:
        themes: Dict[str, Dict[str, str]] = json.load(f)

    EXTENSION_NAME = "extension"

    if style in themes:
        theme = themes[style]
        for language in languages:
            origin_css_file = os.path.join(syntaxlight_path, "css", f"{language}.css")
            if not os.path.exists(origin_css_file):
                print(f"no {language} css file")
                exit(1)
            with open(origin_css_file, "r", encoding="utf-8") as f:
                css_content = f.read()

            # 应用扩展, 完善 CSS
            if EXTENSION_NAME in theme:
                if language in theme[EXTENSION_NAME]:
                    for class_name, css in theme[EXTENSION_NAME][language].items():
                        css_content += "\n" + class_name + " {\n    " + css + "\n}"

            # 使用主题颜色替换 css 文件中的对应类型
            for type_name, color in theme.items():
                if type_name == EXTENSION_NAME:
                    continue

                css_content = css_content.replace(type_name, color)

            with open(export_name, "w", encoding="utf-8") as f:
                f.write(css_content)
    else:
        print(f"unknown style {style}")
        print(f"supported style: {list(themes.keys())}")
        exit(1)
