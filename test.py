import os
import syntaxlight
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--type','-t',type=str,default='c')
parser.add_argument('--index','-i',type=int,default=0)
parser.add_argument('--style','-s',type=str,default='vscode')
parser.add_argument('--lexer',action='store_true')
args = parser.parse_args()

test_folder_path = './test'
languages = os.listdir(test_folder_path)

FILE_TYPE = args.type
INDEX = args.index - 1
STYLE = args.style
LEXER_TEST = args.lexer
TEST_FILES = {}

for language in languages:
    if language != FILE_TYPE:
        continue
    files = os.listdir(os.path.join(test_folder_path, language))
    files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))
    for i in range(len(files)):
        files[i] = os.path.join(test_folder_path, language, files[i])
    TEST_FILES[language] = files


for language, files in TEST_FILES.items():
    if INDEX != -1:
        if LEXER_TEST:
            with open(files[INDEX], 'r',encoding='utf-8') as f:
                lexer = syntaxlight.get_lexer(f.read(),FILE_TYPE)
                tokens = syntaxlight.get_tokens(lexer)
                for token in tokens:
                    print(token)
            break
        syntaxlight.example_display(files[INDEX], STYLE,save_ast_tree=True, show_error_trace=True)
    else:
        syntaxlight.example_display(files, STYLE)
