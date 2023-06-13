
import unittest
import os
import syntaxlight


FILE_TYPES = ['json']


test_folder_path = './test'
languages = os.listdir(test_folder_path)

TEST_FILES = {}

for language in languages:
    if language not in FILE_TYPES:
        continue
    files = os.listdir(os.path.join(test_folder_path, language))
    for i in range(len(files)):
        files[i] = os.path.join(test_folder_path, language, files[i])
    TEST_FILES[language] = files


class TestMyMdParser(unittest.TestCase):

    def test_number_lexer(self):

        for language, files in TEST_FILES.items():
            for file in files:
                print('file = ', file)
                syntaxlight.parse_file(file, language)


if __name__ == "__main__":
    unittest.main()
