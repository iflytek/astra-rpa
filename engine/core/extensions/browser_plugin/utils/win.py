import json
import os
import winreg as reg

import psutil


class Registry:
    @staticmethod
    def exist(key_path) -> bool:
        """
        检测注册表是否存在
        """
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ)
            reg.CloseKey(key)
            return True
        except Exception as e:
            return False

    @staticmethod
    def create(key_path):
        """
        创建项
        """
        keys = key_path.split("\\")
        head_key = reg.OpenKey(reg.HKEY_CURRENT_USER, keys[0], 0, reg.KEY_ALL_ACCESS)
        opened_keys = list()
        opened_keys.append(head_key)
        for key in keys[1:]:
            head_key = reg.CreateKey(head_key, key)
            opened_keys.append(head_key)
        opened_keys.reverse()
        for opened_key in opened_keys:
            reg.CloseKey(opened_key)

    @staticmethod
    def delete(key_path, sub_key):
        """
        删除项
        """
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        # 删除子项
        reg.DeleteKey(key, sub_key)
        reg.CloseKey(key)

    @staticmethod
    def add_string_value(key_path, value_name, value):
        """
        添加字符串kv对
        """
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, value_name, 0, reg.REG_SZ, value)
        reg.CloseKey(key)

    @staticmethod
    def add_dword_value(key_path, value_name, value):
        """
        添加dword kv对
        """
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, value_name, 0, reg.REG_DWORD, value)
        reg.CloseKey(key)

    @staticmethod
    def query_value_ex(key, value_name):
        """
        查询注册表值
        """
        try:
            return reg.QueryValueEx(key, value_name)
        except FileNotFoundError:
            return None, None

    @staticmethod
    def query_value(key_path):
        """
        查询注册表值
        """
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ) as key:
                values = []
                i = 0
                while True:
                    try:
                        value_name, value_data, value_type = reg.EnumValue(key, i)
                        values.append(value_data)
                        i += 1
                    except OSError:
                        break
                # print(f"ExtensionInstallAllowlist下的所有值: {values}")
                return values
        except FileNotFoundError:
            return []

    @staticmethod
    def open_key(key_path):
        """
        打开注册表键
        """
        try:
            return reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            raise FileNotFoundError(f"注册表键 {key_path} 不存在。")


def kill_process(name: str):
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if "{}.exe".format(name) == proc.info["name"].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def check_chrome_plugin(preferences_path_list, extension_id):
    """
    检查类 chrome 浏览器插件的安装状态
    :return: 插件是否安装，安装版本
    """
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, encoding="utf8") as f:
                content = f.read()
                dict_msg = json.loads(content)
                try:
                    extension_info = dict_msg["extensions"]["settings"]
                    if extension_id in extension_info:
                        version = extension_info[extension_id].get("manifest", {}).get("version", "")
                        return True, version
                    else:
                        return False, None
                except KeyError:
                    return False, None

    return False, None


def remove_browser_setting(preferences_path_list, secure_preferences, extension_id):
    """
    删除preferences中插件信息
    :return:
    """
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, encoding="utf8") as f:
                content = f.read()
                dict_msg = json.loads(content)
                uninstall_list = (
                    dict_msg.get("extensions").get("external_uninstalls", []) if dict_msg.get("extensions") else []
                )
                is_update = False
                if extension_id in uninstall_list:
                    uninstall_list.remove(extension_id)
                    is_update = True

                invalid_ids = (
                    dict_msg.get("install_signature").get("invalid_ids", [])
                    if dict_msg.get("install_signature")
                    else []
                )
                if extension_id in invalid_ids:
                    invalid_ids.remove(extension_id)
                    is_update = True

                apps = dict_msg.get("updateclientdata").get("apps", {}) if dict_msg.get("updateclientdata") else {}
                if extension_id in apps:
                    del apps[extension_id]
                    is_update = True

                if is_update:
                    with open(file, "w", encoding="utf8") as f:
                        json.dump(dict_msg, f)
            break

    # 删除用户偏好设置
    if os.path.exists(secure_preferences):
        os.remove(secure_preferences)
