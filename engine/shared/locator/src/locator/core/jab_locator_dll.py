import ctypes
import os
import sys
from ctypes import *

# 初始化dll
jab_path = os.path.join(os.path.dirname(__file__), "exes", "jab")
sys.path.append(jab_path)

lib_windows_access_bridge_path = os.path.join(jab_path, "artifacts", "dll", "win", "libwindowsaccessbridge.dll")
inject_dll_path = os.path.join(jab_path, "artifacts", "dll", "inject", "Inject.dll")
jar_inject_dll_path = os.path.join(jab_path, "artifacts", "dll", "javahook", "IflyrpaJavaHook.dll")

user32 = ctypes.windll.user32
bridge_dll = cdll.LoadLibrary(lib_windows_access_bridge_path)

MAX_STRING_SIZE = 1024
SHORT_STRING_SIZE = 256
MAX_KEY_BINDINGS = 50
MAX_RELATION_TARGETS = 25
MAX_RELATIONS = 5
MAX_ACTION_INFO = 256
MAX_ACTIONS_TO_DO = 32
MAX_VISIBLE_CHILDREN = 256
TIMEOUT = 30
