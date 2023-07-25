from .syntax_parse import parse_file, guess_language
import os
import shutil
from .export import export_css
from typing import Union, List


def example_display(
    file_path: Union[str, List[str]] = None,
    style="vscode",
    save_ast_tree=False,
    language= None,
):
    example_folder_name = os.path.join(os.getcwd(), "syntaxlight_example")
    syntaxlight_path = os.path.dirname(__file__)
    html_template_file = os.path.join(syntaxlight_path, "template.html")
    index_css_file = os.path.join(syntaxlight_path, "css", "index.css")
    css_files = [index_css_file]
    

    example_html_file = os.path.join(example_folder_name, "index.html")

    if not os.path.exists(example_folder_name):
        os.mkdir(example_folder_name)

    if type(file_path) == str:
        file_path = [file_path]

    all_languages = []
    code_html = ""
    for fp in file_path:
        if language is None:
            language = guess_language(fp)
            all_languages.append(language)
        html = parse_file(fp, language, save_ast_tree=save_ast_tree)
        if html is None:
            continue
        code_html += f'<p>{fp}</p><pre class="language-{language}"><code>{html}</code></pre>'

    code_html = f'<div class="markdown-body">{code_html}</div>'

    for language in all_languages:
        css_scope = f"<link rel='stylesheet' href='./{language}.css' />"
        with open(html_template_file, "r", encoding="utf-8") as f:
            content = f.read().replace("html-scope", code_html).replace("css-scope", css_scope)

    with open(os.path.join(example_folder_name, example_html_file), "w", encoding="utf-8") as f:
        f.write(content)

    for file in css_files:
        shutil.copyfile(file, os.path.join(example_folder_name, file.split(os.sep)[-1]))

    export_name = os.path.join(example_folder_name, f"{language}.css")
    export_css([language], export_name, style)
    # print(f"open syntaxlight_example/inedx.html in browser")
