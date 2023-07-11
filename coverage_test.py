
import unittest
import os
import syntaxlight

test_folder_path = './test'
languages = os.listdir(test_folder_path)

TEST_FILES = {}

for language in languages:
    files = os.listdir(os.path.join(test_folder_path, language))
    files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))
    for i in range(len(files)):
        file_path = os.path.join(test_folder_path, language, files[i])
        files[i] = os.path.normpath(file_path)
    TEST_FILES[language] = files

class TestUnit(unittest.TestCase):

    def test_01_json(self):

        for files in TEST_FILES['json']:
            syntaxlight.parse_file(files)

    def test_02_toml(self):

        for files in TEST_FILES['toml']:
            syntaxlight.parse_file(files)

    def test_03_xml(self):

        for files in TEST_FILES['xml']:
            syntaxlight.parse_file(files)


if __name__ == "__main__":
    unittest.main()
