import importlib_metadata

# 获取所有已安装的分发包
packages = importlib_metadata.distributions()

# 创建一个字典来存储包名和版本号
package_info = {}

for package in packages:
    name = package.metadata.get("Name", None)
    version = package.version
    if not name:
        continue
