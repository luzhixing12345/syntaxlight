

import syntaxlight

code = ''

with open('./test/c.c', 'r', encoding='utf-8') as f:
    code = f.read()

c_lexer = syntaxlight.CLexer(code)
token = c_lexer.get_next_token()

while token.type.value != 'EOF':
    print(token)
    token = c_lexer.get_next_token()