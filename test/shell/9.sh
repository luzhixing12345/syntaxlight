$ zood
zood使用方法见 https://luzhixing12345.github.io/zood/

  zood init         初始化仓库
  zood new A B      创建A目录下的B文件
  zood new A        创建根目录下的A文件
  zood update       更新dir.yml顺序
  zood -g           生成docs/目录
  zood clean        删除docs/目录
  zood config       获取配置文件
  zood -s           更新配置文件
其他:
  zood poetry <choice>   更新PYPI库版本
             choice = None(default) 发布版本更新
             choice = sub           次版本更新
             choice = main          主版本更新
  zood vsce <choice>     更新Vscode扩展版本
             choice = None(default) 发布版本更新
             choice = sub           次版本更新
             choice = main          主版本更新


sudo apt install build-essential git m4 scons zlib1g zlib1g-dev \
    libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev \
    python3-dev python-is-python3 libboost-all-dev pkg-config libhdf5-dev libpng-dev

git clone https://gem5.googlesource.com/public/gem5

cd gem5
scons build/X86/gem5.opt -j 4