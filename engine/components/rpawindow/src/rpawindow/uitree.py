import platform
import sys

from rpawindow.core import IUITreeCore

if sys.platform == "win32":
    from rpawindow.core_win import UITreeCore

    UITreeCore: IUITreeCore = UITreeCore()
elif platform.system() == "Linux":
    pass
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))
