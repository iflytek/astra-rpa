#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立的 MSAA 拾取与校验模块
整合原有项目中的 MSAA 相关功能，可独立运行，不依赖项目中的其他文件
"""

import ctypes
import ctypes.wintypes
import traceback

import comtypes
import comtypes.automation
import comtypes.client
import uiautomation as auto
from pywin.mfc.object import Object

from .. import IElement, PickerDomain, Point, Rect
from ..logger import logger
from ..utils.cv import screenshot
from ..utils.process import get_process_name
from .uia_picker import UIAOperate

# 加载 MSAA 相关的 COM 类型库
try:
    comtypes.client.GetModule("oleacc.dll")
except Exception as e:
    logger.info(f"msaa加载异常 {e}")

# MSAA 角色名称映射
ACC_ROLE_NAME_MAP = {
    1: "TitleBar",
    2: "MenuBar",
    3: "ScrollBar",
    4: "Grip",
    5: "Sound",
    6: "Cursor",
    7: "Caret",
    8: "Alert",
    9: "Window",
    10: "Client",
    11: "PopupMenu",
    12: "MenuItem",
    13: "Tooltip",
    14: "Application",
    15: "Document",
    16: "Pane",
    17: "Chart",
    18: "Dialog",
    19: "Border",
    20: "Grouping",
    21: "Separator",
    22: "ToolBar",
    23: "StatusBar",
    24: "Table",
    25: "ColumnHeader",
    26: "RowHeader",
    27: "Column",
    28: "Row",
    29: "Cell",
    30: "Link",
    31: "HelpBalloon",
    32: "Character",
    33: "List",
    34: "ListItem",
    35: "Outline",
    36: "OutlineItem",
    37: "PageTab",
    38: "PropertyPage",
    39: "Indicator",
    40: "Graphic",
    41: "Text",
    42: "EditableText",
    43: "PushButton",
    44: "CheckBox",
    45: "RadioButton",
    46: "ComboBox",
    47: "DropDown",
    48: "ProgressBar",
    49: "Dial",
    50: "HotKeyField",
    51: "Slider",
    52: "SpinBox",
    53: "Diagram",
    54: "Animation",
    55: "Equation",
    56: "DropDownButton",
    57: "MenuButton",
    58: "GridDropDownButton",
    59: "WhiteSpace",
    60: "PageTabList",
    61: "Clock",
    62: "SplitButton",
    63: "IPAddress",
}

# 可读类型映射
WIN32_CONTROL_TYPE = {
    "ListItem": "列表项",
    "List": "列表",
    "Button": "按钮",
    "Text": "文本",
    "ToolBar": "工具栏",
    "MenuItem": "菜单项",
    "Window": "窗口",
    "PushButton": "按钮",
    "EditableText": "可编辑文本",
    "CheckBox": "复选框",
    "RadioButton": "单选按钮",
    "ComboBox": "组合框",
    "DropDown": "下拉框",
    "ProgressBar": "进度条",
    "Slider": "滑块",
    "SpinBox": "数字调节器",
    "Dialog": "对话框",
    "Pane": "面板",
    "Client": "客户区",
    "Application": "应用程序",
    "Document": "文档",
}


class MSAAElement(IElement):
    """
    MSAA 元素封装类
    基于原有的 Element 类，提供 MSAA 元素的基本操作功能
    """

    def __init__(self, iaElement=None, pid=None):
        self.__rect = None  # cache rect
        self.__tag = None
        self.ia_ele = iaElement
        self.pid = pid

    def tag(self) -> str:
        if self.__tag is None:
            tag = self.ia_ele.accRoleName()
            if WIN32_CONTROL_TYPE.get(tag):
                tag = WIN32_CONTROL_TYPE.get(tag)
            self.__tag = tag
        return self.__tag

    def path(self, svc=None, strategy_svc=None):
        self_img = screenshot(self.__rect) if self.__rect else None
        path_list = MSAAPickerUtil.get_element_path(self.ia_ele)
        res = {
            "version": "1",
            "type": PickerDomain.MSAA.value,
            "app": get_process_name(self.pid),
            "path": path_list,
            "img": {"self": self_img},
        }
        return res

    def rect(self) -> Rect:
        self.__rect = MSAAPickerUtil.get_rect(self.ia_ele)
        return self.__rect


class IAElement(Object):
    """
    MSAA 元素封装类
    基于原有的 Element 类，提供 MSAA 元素的基本操作功能
    """

    def __init__(self, IAccessible, iObjectId):
        if not isinstance(iObjectId, int):
            error_msg = "MSAAElement(IAccessible,iObjectId) second argument type must be int"
            raise TypeError(error_msg)
        self.IAccessible = IAccessible
        self.iObjectId = iObjectId
        self.dictCache = {}
        self.__rect = None  # cache rect
        self.__tag = None

    def accChildCount(self):
        """获取子元素数量"""
        if self.iObjectId == 0:
            return self.IAccessible.accChildCount
        else:
            return 0

    def accRole(self):
        """获取元素角色"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        objRole = comtypes.automation.VARIANT()
        objRole.vt = comtypes.automation.VT_BSTR
        self.IAccessible._IAccessible__com__get_accRole(objChildId, objRole)
        return objRole.value

    def accName(self, objValue=None):
        """获取元素名称"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        if objValue is None:
            objName = comtypes.automation.BSTR()
            self.IAccessible._IAccessible__com__get_accName(objChildId, ctypes.byref(objName))
            return objName.value
        else:
            self.IAccessible._IAccessible__com__set_accName(objChildId, objValue)

    def accLocation(self):
        """获取元素位置，返回 (left, top, width, height)"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        objL, objT = ctypes.c_long(), ctypes.c_long()
        objW, objH = ctypes.c_long(), ctypes.c_long()
        self.IAccessible._IAccessible__com_accLocation(
            ctypes.byref(objL),
            ctypes.byref(objT),
            ctypes.byref(objW),
            ctypes.byref(objH),
            objChildId,
        )
        return (objL.value, objT.value, objW.value, objH.value)

    def accValue(self, objValue=None):
        """获取元素值"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        objBSTRValue = comtypes.automation.BSTR()
        if objValue is None:
            self.IAccessible._IAccessible__com__get_accValue(objChildId, ctypes.byref(objBSTRValue))
            return objBSTRValue.value
        else:
            objBSTRValue.value = objValue
            self.IAccessible._IAccessible__com__set_accValue(objChildId, objValue)
            return objBSTRValue.value

    def accDefaultAction(self):
        """获取元素默认动作名称"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        objDefaultAction = comtypes.automation.BSTR()
        self.IAccessible._IAccessible__com__get_accDefaultAction(objChildId, ctypes.byref(objDefaultAction))
        return objDefaultAction.value

    def accDescription(self):
        """获取元素描述"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        objDescription = comtypes.automation.BSTR()
        self.IAccessible._IAccessible__com__get_accDescription(objChildId, ctypes.byref(objDescription))
        return objDescription.value

    def accState(self):
        """获取元素状态"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        objState = comtypes.automation.VARIANT()
        self.IAccessible._IAccessible__com__get_accState(objChildId, ctypes.byref(objState))
        return objState.value

    def accParent(self):
        """获取父元素"""
        objParent = self.IAccessible.accParent
        if objParent is not None:
            return IAElement(objParent, 0)

    def accDoDefaultAction(self):
        """执行元素默认动作"""
        objChildId = comtypes.automation.VARIANT()
        objChildId.vt = comtypes.automation.VT_I4
        objChildId.value = self.iObjectId
        self.IAccessible._IAccessible__com_accDoDefaultAction(objChildId)

    def accRoleName(self):
        """获取角色名称"""
        try:
            iRole = self.accRole()
            return ACC_ROLE_NAME_MAP.get(iRole)
        except:
            return None

    def accHwnd(self):
        """获取元素句柄"""
        hwnd = ctypes.c_long()
        ctypes.oledll.oleacc.WindowFromAccessibleObject(self.IAccessible, ctypes.byref(hwnd))
        return hwnd.value

    def __iter__(self):
        """迭代所有子元素"""
        if self.iObjectId > 0:
            return
        objAccChildArray = (comtypes.automation.VARIANT * self.IAccessible.accChildCount)()
        objAccChildCount = ctypes.c_long()
        ctypes.oledll.oleacc.AccessibleChildren(
            self.IAccessible,
            0,
            self.IAccessible.accChildCount,
            objAccChildArray,
            ctypes.byref(objAccChildCount),
        )
        for i in range(objAccChildCount.value):
            objAccChild = objAccChildArray[i]
            if objAccChild.vt == comtypes.automation.VT_DISPATCH:
                accessible_obj = objAccChild.value.QueryInterface(comtypes.gen.Accessibility.IAccessible)
                yield IAElement(accessible_obj, 0)
            else:
                yield IAElement(self.IAccessible, objAccChild.value)

    def __str__(self):
        """格式化元素信息"""
        iRole = self.accRole()
        role_name = ACC_ROLE_NAME_MAP.get(iRole, "Unkown")
        child_count = self.IAccessible.accChildCount
        return "[%s(0x%X)|%r|ChildCount:%d]" % (
            role_name,
            iRole,
            self.accName(),
            child_count,
        )

    def match_by_rect(self, x, y):
        """根据坐标匹配元素"""
        bMatched = True
        try:
            rect = self.accLocation()
            if rect[2] <= 0 or rect[3] <= 0:
                bMatched = False
            if (rect[0] > x) or ((rect[0] + rect[2]) < x) or (rect[1] > y) or ((rect[1] + rect[3]) < y):
                bMatched = False
        except Exception as ex:
            logger.info(f"通过match_by_rect匹配出错{ex}")
            bMatched = False
        return bMatched

    def finditer_by_rect(self, x, y):
        """根据坐标精确查找元素"""
        parentElement = self
        location = (0, 0, 0, 0)
        while parentElement.accLocation() != location:
            location = parentElement.accLocation()
            for child in list(parentElement):
                if child.match_by_rect(x, y):
                    parentElement = child
                    break
        return parentElement


class MSAAPickerUtil:
    """
    MSAA 拾取器类
    提供 MSAA 元素的拾取和校验功能
    """

    @staticmethod
    def point(x, y):
        """根据坐标点获取 MSAA 元素"""
        objPoint = ctypes.wintypes.POINT()
        objPoint.x = x
        objPoint.y = y
        IAccessible = ctypes.POINTER(comtypes.gen.Accessibility.IAccessible)()
        objChildId = comtypes.automation.VARIANT()
        ctypes.oledll.oleacc.AccessibleObjectFromPoint(objPoint, ctypes.byref(IAccessible), ctypes.byref(objChildId))
        return IAElement(IAccessible, objChildId.value or 0)

    @staticmethod
    def window(objHandle):
        """根据窗口句柄获取 MSAA 元素"""
        if objHandle in (0, None):
            objElement = MSAAPickerUtil.window(ctypes.windll.user32.GetDesktopWindow())
        elif isinstance(objHandle, str):
            objHandle = str(objHandle)
            iHwnd = ctypes.windll.user32.FindWindowW(objHandle, None) or ctypes.windll.user32.FindWindowW(
                None, objHandle
            )
            assert iHwnd > 0, "Cannot FindWindow %r" % objHandle
            objElement = MSAAPickerUtil.window(iHwnd)
        elif isinstance(objHandle, int):
            iHwnd = objHandle
            IAccessible = ctypes.POINTER(comtypes.gen.Accessibility.IAccessible)()
            ctypes.oledll.oleacc.AccessibleObjectFromWindow(
                iHwnd,
                0,
                ctypes.byref(comtypes.gen.Accessibility.IAccessible._iid_),
                ctypes.byref(IAccessible),
            )
            objElement = IAElement(IAccessible, 0)
        else:
            raise TypeError("window argument objHandle must be a int/str/unicode, not %r" % objHandle)
        return objElement

    @staticmethod
    def get_name(ctrl):
        """获取控件名称"""
        try:
            acc_name = ctrl.accName()
            if not acc_name:
                return ""
            return acc_name
        except:
            return ""

    @staticmethod
    def get_type(ctrl):
        """获取控件类型"""
        role_name = ctrl.accRoleName()
        if not role_name:
            role_name = "MSAA"
        return role_name

    @staticmethod
    def get_value(ctrl):
        """获取控件值"""
        try:
            acc_value = ctrl.accValue()
            if not acc_value:
                return ""
            return acc_value
        except:
            return ""

    @staticmethod
    def get_rect(ctrl):
        """获取控件矩形区域"""
        try:
            bound = ctrl.accLocation()
        except:
            bound = [0, 0, 0, 0]
        right = bound[0] + bound[2]
        bottom = bound[1] + bound[3]
        rect = Rect(bound[0], bound[1], right, bottom)
        return rect

    @staticmethod
    def get_hwnd(ctrl):
        """获取控件句柄"""
        return ctrl.accHwnd()

    @staticmethod
    def get_parent(ctrl):
        """获取父控件"""
        return ctrl.accParent()

    @staticmethod
    def has_children(ctrl):
        """判断是否有子控件"""
        children_len = ctrl.accChildCount()
        return children_len > 0

    @staticmethod
    def get_children(ctrl):
        """获取子控件"""
        for child in list(ctrl):
            yield child

    @staticmethod
    def get_control_by_point(x, y):
        """根据坐标获取控件"""
        try:
            # 首先尝试直接获取点击位置的元素
            control = MSAAPickerUtil.point(x, y)
            # 通过迭代寻找最精确的元素
            control = control.finditer_by_rect(x, y)
            return control
        except Exception as e:
            logger.info("获取控件时出错: {}".format(str(e)))
            return None

    @staticmethod
    def get_msaa_element_index(element):
        """计算 MSAA 元素在其兄弟元素中的索引"""
        try:
            parent = element.accParent()
            if not parent:
                logger.info(f"调试: 元素 {element.accName()} 没有父元素")
                return 0

            # logger.info(f"调试: 计算元素 {element.accName()} 的索引，父元素: {parent.accName()}")

            # 获取当前元素的特征信息用于比较
            current_name = element.accName() or ""
            current_role = element.accRole() if hasattr(element, "accRole") else None
            current_location = None
            try:
                current_location = element.accLocation()
            except:
                pass

            index = 0
            sibling_count = 0
            # 使用现有的迭代方法遍历兄弟元素
            for sibling in parent:
                sibling_count += 1
                sibling_name = sibling.accName() or ""
                sibling_role = sibling.accRole() if hasattr(sibling, "accRole") else None
                sibling_location = None
                try:
                    sibling_location = sibling.accLocation()
                except:
                    pass

                # logger.info(f"调试: 兄弟元素 {sibling_count}: {sibling_name}, 当前元素: {current_name} {current_location}")

                # 使用多种条件进行比较
                is_match = False

                # 方法1: 如果位置信息可用，使用位置比较（最准确）
                if current_location and sibling_location:
                    if current_location == sibling_location:
                        is_match = True
                        # logger.info(f"调试: 通过位置匹配找到元素，索引: {index}")

                # 方法2: 如果位置不可用，使用角色+名称+对象地址组合
                elif not is_match:
                    if (
                        current_name == sibling_name and current_role == sibling_role and current_name != ""
                    ):  # 避免空名称的误匹配
                        # 进一步验证：检查是否是同一个对象
                        if sibling.IAccessible == element.IAccessible and sibling.iObjectId == element.iObjectId:
                            is_match = True
                            # logger.info(f"调试: 通过角色+名称+对象地址匹配找到元素，索引: {index}")

                # 方法3: 如果名称为空，仅使用对象地址和ID比较
                elif not is_match and current_name == "":
                    if sibling.IAccessible == element.IAccessible and sibling.iObjectId == element.iObjectId:
                        is_match = True
                        # logger.info(f"调试: 通过对象地址匹配找到元素，索引: {index}")

                if is_match:
                    return index

                index += 1

            # logger.info(f"调试: 未找到匹配元素，总共检查了 {sibling_count} 个兄弟元素")
            return 0
        except Exception as e:
            logger.info("获取MSAA元素索引时出错: {}".format(str(e)))
            logger.info("异常堆栈信息:")
            logger.info(traceback.format_exc())
            return 0

    @staticmethod
    def get_element_info(ctrl):
        """获取元素的详细信息"""
        if not ctrl:
            return None

        try:
            info = {
                "name": MSAAPickerUtil.get_name(ctrl),
                "type": MSAAPickerUtil.get_type(ctrl),
                "value": MSAAPickerUtil.get_value(ctrl),
                "index": MSAAPickerUtil.get_msaa_element_index(ctrl),
            }
            return info
        except Exception as e:
            logger.info("获取元素信息时出错: {}".format(str(e)))
            logger.info("异常堆栈信息:")
            logger.info(traceback.format_exc())
            return None

    @staticmethod
    def get_element_path(ctrl):
        """获取元素的路径信息"""

        def index_of_control(control) -> int:
            index = 0
            pre = control.GetPreviousSiblingControl()
            while pre:
                index += 1
                pre = pre.GetPreviousSiblingControl()
            return index

        path = []
        current = ctrl
        ancestor = None
        try:
            while current:
                info = {
                    "name": MSAAPickerUtil.get_name(current),
                    "tag_name": MSAAPickerUtil.get_type(current),
                    "value": MSAAPickerUtil.get_value(current),
                    "index": MSAAPickerUtil.get_msaa_element_index(current),
                    "checked": True,
                }
                parent = MSAAPickerUtil.get_parent(current)
                if not parent or MSAAPickerUtil.get_type(current) == "Window":
                    ancestor = current
                    break
                if MSAAPickerUtil.get_type(current) == "Document" and MSAAPickerUtil.get_type(parent) == "Window":
                    ancestor = current
                    path.append(info)
                    break
                path.append(info)
                current = parent
                # 防止无限循环
                if len(path) > 40:
                    logger.info(path)
                    logger.info("当前拾取深度超过20，存在死循环风险")
                    break

        except Exception as e:
            logger.info("获取元素路径时出错: {}".format(str(e)))

        # 第二阶段：使用UIA补足窗口层级信息
        if ancestor:
            try:
                # 获取MSAA控件的句柄
                bottom_hwnd = MSAAPickerUtil.get_hwnd(ancestor)
                if bottom_hwnd:
                    # 转换为UIA控件
                    uia_ele = auto.ControlFromHandle(bottom_hwnd)
                    if uia_ele:
                        # 使用UIA向上遍历获取窗口层级
                        uia_current = uia_ele
                        uia_path = []

                        while uia_current:
                            try:
                                value = uia_current.GetValuePattern().Value  # noqa
                            except Exception:  # noqa
                                value = None
                            uia_info = {
                                "cls": uia_current.ClassName,
                                "name": uia_current.Name,
                                "tag_name": uia_current.ControlTypeName,
                                "index": index_of_control(uia_current),
                                "value": value,
                                "checked": True,
                            }
                            uia_path.append(uia_info)
                            uia_parent = uia_current.GetParentControl()

                            # 检查是否到达桌面或顶层
                            if not uia_parent:
                                break
                            # 检查parent是否到达桌面层级
                            if UIAOperate._is_desktop_element(uia_parent):
                                break

                            uia_current = uia_parent

                            # 防止无限循环
                            if len(uia_path) > 20:
                                logger.info(uia_path)
                                logger.info("UIA窗口层级遍历深度超过20，存在死循环风险")
                                break

                        # 将UIA获取的窗口层级添加到路径前面
                        # logger.info(f'uia_path: {uia_path}')
                        # logger.info(f'path: {path}')
                        uia_path.reverse()
                        path.reverse()
                        path = uia_path + path

            except Exception as e:
                logger.info("使用UIA补足窗口层级时出错: {}".format(str(e)))
                logger.info("异常堆栈信息:")
                logger.info(traceback.format_exc())

        return path


class MSAAPicker:
    @classmethod
    def get_similar_path(cls, strategy_svc, curr_path):
        """用户给定两个相似元素"""
        raise Exception("msaa暂不支持相似元素")

    @classmethod
    def get_element(cls, point: Point, pid, **kwargs):
        # 根据坐标拾取元素
        element = MSAAPickerUtil.get_control_by_point(point.x, point.y)
        if element:
            return MSAAElement(iaElement=element, pid=pid)
        else:
            logger.info("msaa未能拾取到元素")
