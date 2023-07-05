import os
import syntaxlight
import sys

index = int(sys.argv[1]) - 1

FILE_TYPES = ['toml']

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
        syntaxlight.example_display(files[index], language)
        continue
    for file in files:
        print('file = ', file)
        syntaxlight.parse_file(file, language)
