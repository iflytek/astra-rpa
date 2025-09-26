import os
import platform
from ctypes import *

# 加载DLL
script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gbild")
if platform.architecture()[0] == "64bit":
    dll_path = os.path.join(script_dir, "gbild64.dll")
else:
    dll_path = os.path.join(script_dir, "gbild32.dll")
dll = windll.LoadLibrary(dll_path)

# 设置接口返回值类型
dll.getmodel.restype = c_char_p
dll.getserialnumber.restype = c_char_p
dll.getproductiondate.restype = c_char_p
dll.getfirmwareversion.restype = c_char_p
dll.getclientscreenresolution.restype = c_char_p
dll.readstring.restype = c_char_p
dll.encryptstring.restype = c_char_p
dll.decryptstring.restype = c_char_p
dll.getproductionname.restype = c_char_p


# ================ 设备操作
# 打开设备（根据设备序号）
def opendevice(index):
    return dll.opendevice(index)


# 打开设备（根据设备ID）
def opendevicebyid(vid, pid):
    return dll.opendevicebyid(vid, pid)


# 打开设备（根据设备路径）
def opendevicebypath(path):
    return dll.opendevicebypath(bytes(path, "utf-8"))


# 检查设备是否连接
def isconnected():
    return dll.isconnected()


# 关闭设备
def closedevice():
    return dll.closedevice()


# 复位设备
def resetdevice():
    return dll.resetdevice()


# ================ 设备信息
# 获取设备型号
def getmodel():
    return dll.getmodel().decode("utf-8")


# 获取设备序列号
def getserialnumber():
    return dll.getserialnumber().decode("utf-8")


# 获取设备生产日期
def getproductiondate():
    return dll.getproductiondate().decode("utf-8")


# 获取设备固件版本号
def getfirmwareversion():
    return dll.getfirmwareversion().decode("utf-8")


# ================ 键盘操作
# 按下键
def presskeybyname(keyn):
    return dll.presskeybyname(bytes(keyn, "utf-8"))


def presskeybyvalue(keyv):
    return dll.presskeybyvalue(keyv)


# 释放键
def releasekeybyname(keyn):
    return dll.releasekeybyname(bytes(keyn, "utf-8"))


def releasekeybyvalue(keyv):
    return dll.releasekeybyvalue(keyv)


# 按下并释放键
def pressandreleasekeybyname(keyn):
    return dll.pressandreleasekeybyname(bytes(keyn, "utf-8"))


def pressandreleasekeybyvalue(keyv):
    return dll.pressandreleasekeybyvalue(keyv)


# 判断键盘按键状态
def iskeypressedbyname(keyn):
    return dll.iskeypressedbyname(bytes(keyn, "utf-8"))


def iskeypressedbyvalue(keyv):
    return dll.iskeypressedbyvalue(keyv)


# 释放所有键盘按键
def releaseallkey():
    return dll.releaseallkey()


# 输入字符串
def inputstring(str):
    return dll.inputstring(bytes(str, "utf-8"))


# 获取大写锁定状态
def getcapslock():
    return dll.getcapslock()


# 获取数字键盘锁定状态
def getnumlock():
    return dll.getnumlock()


# 设置是否区分大小写
def setcasesensitive(cs):
    return dll.setcasesensitive(cs)


# 设置按键延时
def setpresskeydelay(maxd, mind):
    return dll.setpresskeydelay(maxd, mind)


# 设置输入字符串间隔时间
def setinputstringintervaltime(maxd, mind):
    return dll.setinputstringintervaltime(maxd, mind)


# ================ 鼠标操作
# 按下鼠标键
def pressmousebutton(mbtn):
    return dll.pressmousebutton(mbtn)


# 释放鼠标键
def releasemousebutton(mbtn):
    return dll.releasemousebutton(mbtn)


# 按下并释放鼠标键
def pressandreleasemousebutton(mbtn):
    return dll.pressandreleasemousebutton(mbtn)


# 判断鼠标按键状态
def ismousebuttonpressed(mbtn):
    return dll.ismousebuttonpressed(mbtn)


# 释放所有鼠标按键
def releaseallmousebutton():
    return dll.releaseallmousebutton()


# 相对移动鼠标
def movemouserelative(x, y):
    return dll.movemouserelative(x, y)


# 移动鼠标到指定坐标
def movemouseto(x, y):
    return dll.movemouseto(x, y)


# 获取鼠标当前位置
def getmousex():
    return dll.getmousex()


def getmousey():
    return dll.getmousey()


# 移动鼠标滚轮
def movemousewheel(z):
    return dll.movemousewheel(z)


# 设置鼠标按键延时
def setpressmousebuttondelay(maxd, mind):
    return dll.setpressmousebuttondelay(maxd, mind)


# 设置鼠标移动延时
def setmousemovementdelay(maxd, mind):
    return dll.setmousemovementdelay(maxd, mind)


# 设置鼠标移动速度
def setmousemovementspeed(speedvalue):
    return dll.setmousemovementspeed(speedvalue)


# 设置鼠标移动模式
def setmousemovementmode(modevalue):
    return dll.setmousemovementmode(modevalue)


# ================ 双机互联接口
# 设置鼠标当前位置（针对不支持绝对值的鼠标）
def setmouseposition(x, y):
    return dll.setmouseposition(x, y)


# 设置鼠标绝对位置（针对支持绝对值的鼠标）
def setmouseabsoluteposition(x, y):
    return dll.setmouseabsoluteposition(x, y)


# 设置被控端屏幕分辨率
def setclientscreenresolution(width, height):
    return dll.setclientscreenresolution(width, height)


# 获取被控端屏幕分辨率
def getclientscreenresolution():
    return dll.getclientscreenresolution().decode("utf-8")


# ================ 加密狗操作
# 初始化加密狗
def initializedongle():
    return dll.initializedongle()


# 设置读密码
def setreadpassword(writepwd, newpwd):
    return dll.setreadpassword(bytes(writepwd, "utf-8"), bytes(newpwd, "utf-8"))


# 设置写密码
def setwritepassword(oldpwd, newpwd):
    return dll.setwritepassword(bytes(oldpwd, "utf-8"), bytes(newpwd, "utf-8"))


# 从设备读字符串
def readstring(readpwd, addr, count):
    return dll.readstring(bytes(readpwd, "utf-8"), addr, count).decode("utf-8")


# 将字符串写入设备
def writestring(writepwd, str, addr):
    return dll.writestring(bytes(writepwd, "utf-8"), bytes(str, "utf-8"), addr)


# 设置密钥
def setcipher(writepwd, cipher):
    return dll.setcipher(bytes(writepwd, "utf-8"), bytes(cipher, "utf-8"))


# 加密字符串
def encryptstring(str):
    return dll.encryptstring(bytes(str, "utf-8")).decode("utf-8")


# 解密字符串
def decryptstring(str):
    return dll.decryptstring(bytes(str, "utf-8")).decode("utf-8")


# ================ 电源控制接口
# 按下电源按钮
def presspowerbutton():
    return dll.presspowerbutton()


# 释放电源按钮
def releasepowerbutton():
    return dll.releasepowerbutton()


# 按下并释放电源按钮
def pressandreleasepowerbutton():
    return dll.pressandreleasepowerbutton()


# 获取电源工作状态
def getpowerstatus():
    return dll.getpowerstatus()


# ================ 设备定义接口
# 修改设备速度
def setspeed(speed):
    return dll.setspeed()


# 修改设备ID
def setdeviceid(vid, pid):
    return dll.setdeviceid(vid, pid)


# 恢复设备默认ID
def restoredeviceid():
    return dll.restoredeviceid()


# 设置产品名称
def setproductname(name):
    return dll.setproductname(bytes(name, "gbk"))


# 获取产品名称
def getproductionname():
    return dll.getproductionname().decode("gbk")
