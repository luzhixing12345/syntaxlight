from .syntax_parse import parse_file
import os
import shutil


def example_display(file_path: str = None, language: str = "guess"):
    example_folder_name = os.path.join(os.getcwd(), "syntaxlight_example")

    syntaxlight_path = os.path.dirname(__file__)
    html_template_file = os.path.join(syntaxlight_path, "template.html")
    syntax_css_file = os.path.join(syntaxlight_path, "css", "syntaxlight.css")
    index_css_file = os.path.join(syntaxlight_path, "css", "index.css")
    language_css_file = os.path.join(syntaxlight_path, "css", f"{language}.css")
    css_files = [syntax_css_file, index_css_file, language_css_file]
    css_scope = f"<link rel='stylesheet' href='./{language}.css' />"

    example_html_file = os.path.join(example_folder_name, "index.html")

    if not os.path.exists(example_folder_name):
        os.mkdir(example_folder_name)

    if type(file_path) == str:
        file_path = [file_path]
    
    code_html = ''
    for fp in file_path:
        html = parse_file(fp, language)
        code_html += f'<pre class="language-{language}"><code>{html}</code></pre>'

    code_html = f'<div class="markdown-body">{code_html}</div>'
    with open(html_template_file, "r", encoding="utf-8") as f:
        content = f.read().replace("html-scope", code_html).replace("css-scope", css_scope)

    with open(os.path.join(example_folder_name, example_html_file), "w", encoding="utf-8") as f:
        f.write(content)

    for file in css_files:
        shutil.copyfile(file, os.path.join(example_folder_name, file.split(os.sep)[-1]))
