import winreg as reg


class Registry:
    """注册表操作"""

    @staticmethod
    def exist(key_path):
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
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, value_name, 0, reg.REG_SZ, value)
        reg.CloseKey(key)

    @staticmethod
    def get_registry_value(key_path, value_name):
        try:
            # 打开注册表键
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path)
            # 获取值
            value, regtype = reg.QueryValueEx(key, value_name)
            # 关闭注册表键
            reg.CloseKey(key)
            return value
        except:
            return None


class AutoStart:
    AUTO_START_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def check(name="iflyrpa"):
        exe_path = Registry.get_registry_value(AutoStart.AUTO_START_KEY_PATH, name)
        if not exe_path or exe_path != exe_path:
            return False
        return True

    @staticmethod
    def enable(exe_path: str, name="iflyrpa"):
        if AutoStart.check(name):
            return
        Registry.create(AutoStart.AUTO_START_KEY_PATH)
        Registry.add_string_value(AutoStart.AUTO_START_KEY_PATH, name, exe_path)

    @staticmethod
    def disable(name="iflyrpa"):
        if not AutoStart.check(name):
            return
        Registry.add_string_value(AutoStart.AUTO_START_KEY_PATH, name, "")
