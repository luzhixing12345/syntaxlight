

import syntaxlight
import sys

file_type = sys.argv[1]
file_name = sys.argv[2]

file_path = f'./test/{file_type}/{file_name}.{file_type}'

code = ''

with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

lexer = syntaxlight.JsonLexer(code)
token = lexer.get_next_token()

while token.type.value != 'EOF':
    print(token)
    token = lexer.get_next_token()