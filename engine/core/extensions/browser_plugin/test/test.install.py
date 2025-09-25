import json
import os
import platform
import subprocess


def install_firefox_extension(extension_id, xpi_url):
    # 根据操作系统确定策略文件位置
    if platform.system() == "Windows":
        policy_dir = os.path.join(os.getenv("ProgramFiles"), "Mozilla Firefox", "distribution")
    elif platform.system() == "Linux":
        policy_dir = "/usr/lib/firefox/distribution"
    elif platform.system() == "Darwin":  # macOS
        policy_dir = "/Applications/Firefox.app/Contents/Resources/distribution"
    else:
        raise OSError("Unsupported operating system")

    # 创建目录如果不存在
    os.makedirs(policy_dir, exist_ok=True)

    # 策略文件内容
    policy = {"policies": {"Extensions": {"Install": [xpi_url], "Uninstall": []}}}

    # 写入策略文件
    policy_path = os.path.join(policy_dir, "policies.json")
    with open(policy_path, "w") as f:
        json.dump(policy, f, indent=2)

    print(f"Firefox extension installation policy created at {policy_path}")


# 使用示例
extension_id = "iflyrpa@iflytek.com"
xpi_url = "C:/Users/gqzheng2/AppData/Local/gqwork/52529c15b9584e6c8be5-5.1.1.xpi"
install_firefox_extension(extension_id, xpi_url)


# Firefox 安装目录 (根据你的系统调整)
firefox_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"

# 插件路径
extension_path = xpi_url

# 使用 Firefox 命令行安装插件
subprocess.run([firefox_path, extension_path])
