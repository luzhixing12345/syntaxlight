import os
import syntaxlight
import sys

index = int(sys.argv[1]) - 1
lexer_test = False
if len(sys.argv) == 3:
    lexer_test = True

FILE_TYPES = ['c']

test_folder_path = './test'
languages = os.listdir(test_folder_path)

TEST_FILES = {}

for language in languages:
    if language not in FILE_TYPES:
        continue
    files = os.listdir(os.path.join(test_folder_path, language))
    files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))
    for i in range(len(files)):
        files[i] = os.path.join(test_folder_path, language, files[i])
    TEST_FILES[language] = files


for language, files in TEST_FILES.items():
    if index != -1:
        if lexer_test:
            with open(files[index], 'r',encoding='utf-8') as f:
                lexer = syntaxlight.get_lexer(f.read(),FILE_TYPES[0])
                tokens = syntaxlight.get_tokens(lexer)
                # for token in tokens:
                #     print(token)
            break
        syntaxlight.example_display(files[index], language)
        continue
    for file in files:
        print('file = ', file)
        syntaxlight.parse_file(file, language)
