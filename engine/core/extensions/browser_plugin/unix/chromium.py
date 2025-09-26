import json
import os
import subprocess

from ..constants import PluginData, PluginStatus
from ..core import PluginManagerCore

# 使用 Chromium 内核的浏览器在 linux 中的插件安装策略都出差不多，统一抽象成一个类

# chrome 在 linux 中安装插件的方法：
# https://developer.chrome.com/docs/extensions/how-to/distribute/install-extensions?hl=zh-cn#preference-linux

# Edge 在 linux 中安装插件的方法：
# https://learn.microsoft.com/zh-cn/microsoft-edge/extensions-chromium/developer-guide/alternate-distribution-options#using-a-preferences-json-file-macos-and-linux


class ChromiumPluginManager(PluginManagerCore):
    root_path = "/opt/google/chrome"  # 浏览器的安装路径
    browser_name = "google-chrome"  # 浏览器的名称
    process_name = "chrome"  # 进程的名称
    extension_path = os.path.join(root_path, "extensions")

    def __init__(
        self,
        plugin_data: PluginData,
        root_path: str,
        browser_name: str,
        process_name: str,
    ) -> None:
        self.plugin_data = plugin_data
        self.root_path = root_path
        self.browser_name = browser_name
        self.process_name = process_name
        self.extension_path = os.path.join(root_path, "extensions")

    def check_browser(self):
        try:
            result = subprocess.run(["which", self.browser_name], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def check_plugin(self):
        # 检查插件配置文件是否存在
        plugin_config_path = os.path.join(self.extension_path, f"{self.plugin_data.plugin_id}.json")
        if os.path.exists(plugin_config_path):
            with open(plugin_config_path) as file:
                plugin_config_data = json.load(file)
                installed_version = plugin_config_data.get("external_version")
                latest_version = self.plugin_data.plugin_version
                latest = installed_version == latest_version
                return PluginStatus(
                    installed=True,
                    installed_version=installed_version,
                    latest_version=latest_version,
                    latest=latest,
                )
        else:
            return PluginStatus(
                installed=False,
                latest_version=self.plugin_data.plugin_version,
                latest=False,
            )

    def close_browser(self):
        try:
            # 使用 killall 命令终止所有名为 firefox 的进程
            subprocess.run(["killall", self.process_name], check=True)
            print("Browser has been closed successfully.")
        except subprocess.CalledProcessError:
            print("Failed to close browser. It may not be running.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def install_plugin(self):
        # 检查是否有读写权限
        read_write = os.access(self.root_path, os.R_OK | os.W_OK)
        if not read_write:
            try:
                subprocess.run(["pkexec", "chmod", "777", self.root_path], check=True)
            except subprocess.CalledProcessError as e:
                raise Exception("密码验证失败")

        # 检查路径是否存在
        if not os.path.exists(self.extension_path):
            # 如果路径不存在，使用os.makedirs创建路径
            os.makedirs(self.extension_path)
            print(f"Directory '{self.extension_path}' has been created.")

        plugin_config_data = {
            "external_crx": self.plugin_data.plugin_path,
            "external_version": self.plugin_data.plugin_version,
        }
        plugin_config_path = os.path.join(self.extension_path, f"{self.plugin_data.plugin_id}.json")
        # 写入JSON数据到文件
        with open(plugin_config_path, "w") as file:
            json.dump(plugin_config_data, file, indent=4)  # 使用indent参数美化输出格式

        # 将 policy.json 文件复制到etc/opt/chrome/policies/managed目录下
        policy_dir = "/etc/opt/chrome/policies/managed"
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        policy_json_path = os.path.join(project_root, "policy", "policy.json")
        if not os.path.exists(policy_dir):
            os.makedirs(policy_dir)
        subprocess.run(["sudo", "cp", policy_json_path, policy_dir], check=True)
