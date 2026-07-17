from .syntax_parse import parse_file, guess_language
from html import escape
import os
import shutil
from .export import export_css
from typing import Union, List
import sys


def example_display(file_path: Union[str, List[str]] = None, style="vscode", language=None):
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
    code_sections = []
    navigation_items = []
    for index, fp in enumerate(file_path, start=1):
        current_language = language or guess_language(fp)
        if current_language not in all_languages:
            all_languages.append(current_language)
        parse_result = parse_file(fp, current_language)
        if parse_result.error is not None:
            sys.stderr.write(str(parse_result.error))
        highlighted_code = parse_result.parser.to_html()
        section_id = f"test-case-{index}"
        file_label = os.path.basename(fp)
        case_number = os.path.splitext(file_label)[0]
        code_sections.append(
            f'<section class="code-section" id="{section_id}">'
            f'<p class="code-section-title">{escape(fp)}</p>'
            f'<pre class="language-{current_language}"><code>{highlighted_code}</code></pre>'
            "</section>"
        )
        navigation_items.append(
            f'<li><a href="#{section_id}" title="{escape(file_label)}" '
            f'aria-label="Jump to test {escape(case_number)}">{escape(case_number)}</a></li>'
        )

    navigation_html = ""
    if len(code_sections) > 1:
        navigation_html = (
            '<nav class="test-navigation" aria-label="Test cases"><ol>'
            f'{"".join(navigation_items)}'
            "</ol></nav>"
        )
    code_html = (
        '<div class="preview-layout">'
        f"{navigation_html}"
        f'<main class="markdown-body">{"".join(code_sections)}</main>'
        "</div>"
    )

    css_scope = "\n    ".join(
        f"<link rel='stylesheet' href='./{current_language}.css' />"
        for current_language in all_languages
    )
    with open(html_template_file, "r", encoding="utf-8") as f:
        content = f.read().replace("html-scope", code_html).replace("css-scope", css_scope)

    with open(example_html_file, "w", encoding="utf-8") as f:
        f.write(content)

    for file in css_files:
        shutil.copyfile(file, os.path.join(example_folder_name, file.split(os.sep)[-1]))

    export_css(all_languages, example_folder_name, style)
    print("Generated syntaxlight_example/index.html")
