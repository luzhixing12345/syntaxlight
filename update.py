

'''
这个文件的作用是更新 PYPI 包, 修改 pyproject.toml 的 VERSION 版本号并发布, 相当于 poetry build + poetry publish

使用方法

    python update.py                  发布版本更新
    python update.py sub              次版本更新
    python update.py main             主版本更新

'''



import shutil
import re,os
import sys

def main():
    try:
        shutil.rmtree("dist")
        print('delete dist')
    except:
        pass

    with open('pyproject.toml','r') as f:
        file = f.read()

    version = re.search(r'version = \"(\d+)\.(\d+)\.(\d+)\"',file)
    MAIN_VERSION, SUB_VERSION, FIX_VERSION = int(version.group(1)),int(version.group(2)),int(version.group(3))

    if len(sys.argv) == 1:
        FIX_VERSION = FIX_VERSION + 1
    elif sys.argv[1] == 'sub':
        SUB_VERSION = SUB_VERSION + 1
        FIX_VERSION = 0
    elif sys.argv[1] == 'main':
        MAIN_VERSION = MAIN_VERSION + 1
        SUB_VERSION = 0
        FIX_VERSION = 0

    new_version = f'version = \"{MAIN_VERSION}.{SUB_VERSION}.{FIX_VERSION}\"'
    new_content = re.sub(r'version = \"(\d+)\.(\d+)\.(\d+)\"',new_version,file)
    with open('pyproject.toml','w') as f:
        f.write(new_content)
    
    print(new_version)
    os.system("poetry build")
    os.system("poetry publish")

if __name__ == '__main__':
    main()