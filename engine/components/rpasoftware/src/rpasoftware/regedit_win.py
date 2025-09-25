import win32api
import win32con


class Regedit:
    """封装注册表"""

    def __init__(self, keyname, handle=None, mode="w"):
        if mode == "r":
            access = win32con.KEY_READ | win32con.KEY_WOW64_64KEY
        else:
            access = win32con.WRITE_OWNER | win32con.KEY_WOW64_64KEY | win32con.KEY_ALL_ACCESS
        self.mode = mode
        self.handle = None
        if handle is None:
            handle = win32con.HKEY_CURRENT_USER
        try:
            self.handle = win32api.RegOpenKeyEx(handle, keyname, 0, access)
        except:
            # 可预见错误，没有就创建
            try:
                self.handle = win32api.RegCreateKey(handle, keyname)
            except Exception as e:
                raise Exception("RegCreateKey error {}".format(e))

    def __getattr__(self, name):
        if name[0] == "_":
            raise Exception("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        return self.__class__(name, self.handle, self.mode)

    def __setattr__(self, name, value):
        if name in ("handle", "mode") or name in self.__dict__:
            self.__dict__[name] = value
            return
        self.__getattr__(name)[""] = value

    def __getitem__(self, name):
        try:
            value, types = win32api.RegQueryValueEx(self.handle, name)
            if types == win32con.REG_MULTI_SZ:
                return tuple(value)
            return value
        except Exception as e:
            raise Exception("RegQueryValueEx error {}".format(e))

    def __setitem__(self, name, value):
        try:
            if isinstance(value, (tuple, list)):
                value = list(map(str, value))
                win32api.RegSetValueEx(self.handle, name, None, win32con.REG_MULTI_SZ, value)
            elif isinstance(value, bytes):
                win32api.RegSetValueEx(self.handle, name, None, win32con.REG_SZ, value.decode("UTF8"))
            else:
                win32api.RegSetValueEx(self.handle, name, None, win32con.REG_SZ, str(value))
        except Exception as e:
            raise Exception("RegSetValueEx error {}".format(e))

    def __del__(self):
        if self.handle is not None:
            win32api.RegCloseKey(self.handle)
            self.handle = None
