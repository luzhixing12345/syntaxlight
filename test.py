import argparse
import os
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import syntaxlight


BASE_DIR = Path(__file__).resolve().parent
TEST_DIR = BASE_DIR / "test"
HOST = "127.0.0.1"


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", "-t", default="c", help="language test directory")
    parser.add_argument("--index", "-i", type=int, default=0, help="one-based case index; 0 selects all")
    parser.add_argument("--style", "-s", default="vscode")
    parser.add_argument("--lexer", action="store_true", help="print tokens without starting a server")
    parser.add_argument("--port", "-p", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="start the server without opening a browser")
    return parser


def get_test_files(language, index):
    language_dir = TEST_DIR / language
    if not language_dir.is_dir():
        raise ValueError(f"unsupported test language: {language}")

    files = sorted(
        (path for path in language_dir.iterdir() if path.is_file() and path.stem.isdigit()),
        key=lambda path: int(path.stem),
    )
    if not files:
        raise ValueError(f"no test files found for language: {language}")
    if index < 0 or index > len(files):
        raise ValueError(f"index must be between 0 and {len(files)}")
    return files if index == 0 else [files[index - 1]]


def print_tokens(files, language):
    for file_path in files:
        if len(files) > 1:
            print(f"==> {file_path.relative_to(BASE_DIR)} <==")
        with file_path.open("r", encoding="utf-8") as file:
            lexer = syntaxlight.get_lexer(file.read(), language)
        for token in syntaxlight.get_tokens(lexer):
            print(token)


def serve_example(port, open_browser):
    handler = partial(SimpleHTTPRequestHandler, directory=str(BASE_DIR))
    try:
        server = ThreadingHTTPServer((HOST, port), handler)
    except OSError as error:
        raise RuntimeError(f"cannot start HTTP server on {HOST}:{port}: {error}") from error

    with server:
        url = f"http://{HOST}:{server.server_port}/syntaxlight_example/index.html"
        print(f"Serving syntaxlight preview at {url}")
        print("Press Ctrl+C to stop the server.")
        if open_browser and not webbrowser.open(url):
            print("Could not open a browser automatically; open the URL above manually.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nHTTP server stopped.")


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        files = get_test_files(args.type, args.index)
    except ValueError as error:
        parser.error(str(error))

    if args.lexer:
        print_tokens(files, args.type)
        return

    os.chdir(BASE_DIR)
    input_files = [str(path) for path in files]
    syntaxlight.example_display(input_files[0] if len(input_files) == 1 else input_files, args.style)
    try:
        serve_example(args.port, not args.no_browser)
    except RuntimeError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
