
import unittest
import os
import syntaxlight
import time

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

# 简要输出测试的文件的信息
for language in TEST_FILES:
    print(f"{language}: {len(TEST_FILES[language])} files")

time.sleep(3)

class TestUnit(unittest.TestCase):
    
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.file_types = syntaxlight.supported_languages

    def test_coverage(self):
        
        for language in self.file_types:
            for file_path in TEST_FILES[language]:
                syntaxlight.parse_file(file_path, language)


if __name__ == "__main__":
    unittest.main()
