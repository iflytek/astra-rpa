"""
MSAA定位器模块

提供Microsoft Active Accessibility (MSAA)技术的元素定位功能。
"""

import ctypes
import ctypes.wintypes
from typing import Any, Optional, Union

import comtypes
import comtypes.automation
import comtypes.client
from locator import ILocator, Rect
from locator.core.uia_locator import uia_factory
from rpaframe.logger.logger import logger

# 加载MSAA相关库
comtypes.client.GetModule("oleacc.dll")
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


class MSAALocator(ILocator):
    """
    MSAA定位器类

    用于封装MSAA元素并提供统一的定位接口。
    """

    def __init__(self, ia_element):
        """初始化MSAA定位器

        Args:
            ia_element: MSAA元素对象
        """
        self.__rect = ia_element.get_rect()
        self.ia_element = ia_element

    def rect(self) -> Optional[Rect]:
        logger.info(f"msaa获取到的矩形区域: {self.__rect.to_json()}")
        return self.__rect

    def control(self) -> Any:
        return self.ia_element


class MSAAElement:
    """MSAA元素包装类"""

    def __init__(self, IAccessible, iObjectId):
        if not isinstance(iObjectId, int):
            raise TypeError("iObjectId必须是整数类型")
        self.IAccessible = IAccessible
        self.iObjectId = iObjectId
        self.dictCache = {}

    @property
    def name(self):
        return self.get_name()

    def get_acc_role(self):
        """获取元素角色"""
        obj_child_id = comtypes.automation.VARIANT()
        obj_child_id.vt = comtypes.automation.VT_I4
        obj_child_id.value = self.iObjectId
        obj_role = comtypes.automation.VARIANT()
        obj_role.vt = comtypes.automation.VT_BSTR
        self.IAccessible._IAccessible__com__get_accRole(obj_child_id, obj_role)
        return obj_role.value

    def get_acc_role_name(self):
        """获取角色名称"""
        try:
            role_id = self.get_acc_role()
            return ACC_ROLE_NAME_MAP.get(role_id)
        except Exception as e:
            logger.info(f"获取tag_name出现异常{e}")
            return None

    def get_type(self):
        """获取控件类型"""
        # logger.info(f'获取控件类型 start ')
        role_name = self.get_acc_role_name()
        if not role_name:
            role_name = "MSAA"
        # logger.info(f'获取控件类型 end {role_name}')
        return role_name

    def get_name(self):
        """获取元素名称"""
        try:
            obj_child_id = comtypes.automation.VARIANT()
            obj_child_id.vt = comtypes.automation.VT_I4
            obj_child_id.value = self.iObjectId
            obj_name = comtypes.automation.BSTR()
            self.IAccessible._IAccessible__com__get_accName(obj_child_id, ctypes.byref(obj_name))
            return obj_name.value or ""
        except:
            return ""

    def get_value(self):
        """获取元素值"""
        try:
            obj_child_id = comtypes.automation.VARIANT()
            obj_child_id.vt = comtypes.automation.VT_I4
            obj_child_id.value = self.iObjectId
            obj_bstr_value = comtypes.automation.BSTR()
            self.IAccessible._IAccessible__com__get_accValue(obj_child_id, ctypes.byref(obj_bstr_value))
            return obj_bstr_value.value or ""
        except:
            return ""

    def get_role(self):
        """获取元素角色"""
        try:
            obj_child_id = comtypes.automation.VARIANT()
            obj_child_id.vt = comtypes.automation.VT_I4
            obj_child_id.value = self.iObjectId
            obj_role = comtypes.automation.VARIANT()
            obj_role.vt = comtypes.automation.VT_BSTR
            self.IAccessible._IAccessible__com__get_accRole(obj_child_id, obj_role)
            return obj_role.value
        except:
            return None

    def get_location(self):
        """获取元素位置 (left, top, width, height)"""
        try:
            obj_child_id = comtypes.automation.VARIANT()
            obj_child_id.vt = comtypes.automation.VT_I4
            obj_child_id.value = self.iObjectId
            obj_left, obj_top, obj_width, obj_height = (
                ctypes.c_long(),
                ctypes.c_long(),
                ctypes.c_long(),
                ctypes.c_long(),
            )
            self.IAccessible._IAccessible__com_accLocation(
                ctypes.byref(obj_left),
                ctypes.byref(obj_top),
                ctypes.byref(obj_width),
                ctypes.byref(obj_height),
                obj_child_id,
            )
            return (obj_left.value, obj_top.value, obj_width.value, obj_height.value)
        except:
            return (0, 0, 0, 0)

    def get_rect(self):
        """获取控件矩形区域"""
        try:
            bound = self.get_location()
        except Exception as e:
            bound = [0, 0, 0, 0]
        right = bound[0] + bound[2]
        bottom = bound[1] + bound[3]
        rect = Rect(bound[0], bound[1], right, bottom)
        return rect

    def get_parent(self):
        """获取父元素"""
        try:
            objParent = self.IAccessible.accParent
            if objParent is not None:
                return MSAAElement(objParent, 0)
            return None
        except:
            return None

    def get_children(self):
        """获取子元素列表"""
        try:
            if self.iObjectId > 0:
                return []

            child_count = self.IAccessible.accChildCount
            if child_count == 0:
                return []

            objAccChildArray = (comtypes.automation.VARIANT * child_count)()
            objAccChildCount = ctypes.c_long()
            ctypes.oledll.oleacc.AccessibleChildren(
                self.IAccessible,
                0,
                child_count,
                objAccChildArray,
                ctypes.byref(objAccChildCount),
            )

            children = []
            for i in range(objAccChildCount.value):
                objAccChild = objAccChildArray[i]
                if objAccChild.vt == comtypes.automation.VT_DISPATCH:
                    child = MSAAElement(
                        objAccChild.value.QueryInterface(comtypes.gen.Accessibility.IAccessible),
                        0,
                    )
                    children.append(child)
                else:
                    child = MSAAElement(self.IAccessible, objAccChild.value)
                    children.append(child)
            return children
        except:
            return []

    def get_index(self):
        """获取元素在其兄弟元素中的索引"""
        try:
            parent = self.get_parent()
            if not parent:
                logger.info(f"元素 {self.get_name()} 没有父元素")
                return 0

            logger.info(f"计算元素 {self.get_name()} 的索引，父元素: {parent.get_name()}")

            # 获取当前元素的特征信息用于比较
            current_name = self.get_name()
            current_role = self.get_role()
            current_location = self.get_location()
            current_type = self.get_type()

            # 获取所有兄弟元素
            siblings = parent.get_children()

            # 遍历兄弟元素，找到当前元素的位置
            for index, sibling in enumerate(siblings):
                sibling_name = sibling.get_name()
                sibling_role = sibling.get_role()
                sibling_location = sibling.get_location()
                sibling_type = sibling.get_type()

                # 使用多种条件进行比较
                is_match = False

                # 方法1: 如果位置信息可用，使用位置比较（最准确）
                if current_location and sibling_location:
                    if current_location == sibling_location:
                        is_match = True
                        logger.info(f"通过位置匹配找到元素，索引: {index}")

                # 方法2: 如果位置不可用或不匹配，使用角色+名称+类型组合
                if not is_match:
                    if current_name == sibling_name and current_role == sibling_role and current_type == sibling_type:
                        # 进一步验证：检查是否是同一个对象
                        if sibling.IAccessible == self.IAccessible and sibling.iObjectId == self.iObjectId:
                            is_match = True
                            logger.info(f"通过角色+名称+类型+对象地址匹配找到元素，索引: {index}")

                # 方法3: 如果名称为空，仅使用对象地址和ID比较
                if not is_match and current_name == "":
                    if sibling.IAccessible == self.IAccessible and sibling.iObjectId == self.iObjectId:
                        is_match = True
                        logger.info(f"通过对象地址匹配找到元素，索引: {index}")

                if is_match:
                    return index

            logger.info(f"未找到匹配元素，总共检查了 {len(siblings)} 个兄弟元素")
            return 0

        except Exception as e:
            logger.info(f"获取MSAA元素索引时出错: {str(e)}")
            return 0


class MSAAValidator:
    """MSAA元素校验器"""

    @staticmethod
    def _get_msaa_ele_from_hwnd(hwnd, dwObjectID=0):
        """
        通过窗口句柄获取MSAA对象

        Args:
            hwnd: 窗口句柄
            dwObjectID: 对象标识符，默认为OBJID_CLIENT(0)
        """
        # 定义常用的对象ID
        OBJID_CLIENT = 0
        OBJID_WINDOW = -1

        # 如果指定了特定的对象ID，先尝试该ID
        if dwObjectID != 0:
            try:
                IAccessible = ctypes.POINTER(comtypes.gen.Accessibility.IAccessible)()
                ctypes.oledll.oleacc.AccessibleObjectFromWindow(
                    hwnd,
                    dwObjectID,
                    ctypes.byref(comtypes.gen.Accessibility.IAccessible._iid_),
                    ctypes.byref(IAccessible),
                )
                logger.info(f"成功通过对象ID {dwObjectID} 获取MSAA对象")
                return IAccessible
            except Exception as e:
                logger.info(f"通过对象ID {dwObjectID} 获取MSAA对象失败: {e}")

        # 尝试不同的对象ID
        object_ids = [OBJID_CLIENT, OBJID_WINDOW]

        for obj_id in object_ids:
            try:
                IAccessible = ctypes.POINTER(comtypes.gen.Accessibility.IAccessible)()
                ctypes.oledll.oleacc.AccessibleObjectFromWindow(
                    hwnd,
                    obj_id,
                    ctypes.byref(comtypes.gen.Accessibility.IAccessible._iid_),
                    ctypes.byref(IAccessible),
                )
                logger.info(f"成功通过对象ID {obj_id} 获取MSAA对象")
                return IAccessible
            except Exception as e:
                logger.info(f"通过对象ID {obj_id} 获取MSAA对象失败: {e}")
                continue

        logger.info("无法通过任何对象ID获取MSAA对象")
        return None

    @staticmethod
    def _find_matches_in_parent(parent_element, target_desc, use_recursive=False):
        """在父元素中查找匹配目标描述的子元素"""
        matches = []

        try:
            target_name = target_desc.get("name")
            target_value = target_desc.get("value")
            target_index = target_desc.get("index", 0)
            target_tag = target_desc.get("tag_name")

            logger.info(
                f"正在查找: tag_name={target_tag}, name={target_name}, value={target_value}, index={target_index}, use_recursive={use_recursive}"
            )

            # 获取所有子元素
            children = parent_element.get_children()
            logger.info(f"父元素有 {len(children)} 个子元素")

            for i, c in enumerate(children):
                child_type = c.get_type()
                child_name = c.get_name()
                child_value = c.get_value()
                logger.info(f'子元素[{i}]: type={child_type}, name="{child_name}", value="{child_value}"')

            # 筛选匹配类型的子元素
            candidates = [c for c in children if c.get_type() == target_tag]
            logger.info(f"匹配类型 {target_tag} 的候选元素数量: {len(candidates)}")

            # 如果没有直接匹配的子元素，且允许递归搜索，则尝试递归搜索
            if not candidates and use_recursive:
                logger.info(f"没有找到直接匹配的子元素，尝试递归搜索...")
                for child in children:
                    recursive_matches = MSAAValidator._find_matches_in_parent(child, target_desc, use_recursive=True)
                    if recursive_matches:
                        logger.info(f"递归搜索找到匹配元素")
                        return recursive_matches

            # 进一步过滤匹配名称和值的元素
            filtered_candidates = []
            for candidate in candidates:
                name_match = not target_name or candidate.get_name() == target_name
                value_match = not target_value or candidate.get_value() == target_value
                index_match = not target_index or candidate.get_index() == target_index

                logger.info(f"候选元素匹配检查: name_match={name_match}, value_match={value_match}")

                if name_match and value_match and index_match:
                    filtered_candidates.append(candidate)

            logger.info(f"最终过滤后的候选元素数量: {len(filtered_candidates)}")

            # 根据索引选择元素
            if filtered_candidates:
                matches.append(filtered_candidates[0])
                logger.info(f"选择第一个元素")

        except Exception as e:
            logger.info(f"在父元素中查找匹配项时出错: {str(e)}")

        return matches

    @staticmethod
    def find_element_by_msaa_path(path_info, start_element):
        """
        根据路径信息查找元素
        返回 (找到的元素列表, 错误信息)
        """
        # logger.info(
        #     f'msaa 开始的首元素信息 {start_element.get_type()} {start_element.get_name()}  {start_element.get_value()}')

        try:
            if not path_info:
                return [], "路径信息为空"

            current_elements = [start_element]
            path_start_index = 0

            # 逐层级查找子元素
            for depth in range(path_start_index, len(path_info)):
                target_desc = path_info[depth]
                if not current_elements:
                    return [], f"在第{depth}层级查找失败"

                next_elements = []

                # 只在第一层查找时使用递归搜索
                use_recursive = depth == 0
                logger.info(f"第{depth + 1}层级查找，use_recursive={use_recursive}")

                for parent_elem in current_elements:
                    matches = MSAAValidator._find_matches_in_parent(
                        parent_elem, target_desc, use_recursive=use_recursive
                    )
                    next_elements.extend(matches)

                if not next_elements:
                    return (
                        [],
                        f"在第{depth + 1}层级未找到匹配元素: {target_desc['tag_name']} '{target_desc.get('name', '')}'",
                    )

                current_elements = next_elements
                logger.info(f"第{depth + 1}层级查找完成，找到 {len(current_elements)} 个匹配元素")

            return current_elements

        except Exception as e:
            logger.info(f"路径查找异常: {str(e)}")
            return []

    @staticmethod
    def find_element_by_uia_path(ele, picker_type):
        """根据uia元素路径信息查找并置顶应用，返回最后一个元素的句柄信息"""
        hwnd = 0
        try:
            uia_ele = uia_factory.__find_partial_match__(ele, picker_type)
            hwnd = uia_ele.control().NativeWindowHandle
        except Exception as e:
            logger.info(f"在父元素中查找匹配项时出错: {str(e)}")
        return hwnd

    @staticmethod
    def validate(ele: dict, picker_type: str):
        """
        通过路径信息校验元素
        返回 (是否有效, 消息, 找到的元素列表)
        """
        try:
            path = ele["path"]
            logger.info(f"完整路径: {path}")

            uia_path = []
            msaa_path = []
            last_control_index = -1

            for i, item in enumerate(path):
                tag_name = item.get("tag_name", "")
                # logger.info(f'路径项[{i}]: {item}')
                if tag_name.endswith("Control"):
                    last_control_index = i

            logger.info(f"最后一个Control索引: {last_control_index}")

            if last_control_index == -1:
                logger.info("没有找到Control元素，使用UIA路径")
                return uia_factory.__find_one__(ele, picker_type)

            uia_path = path[: last_control_index + 1]
            msaa_path = path[last_control_index + 1 :]

            logger.info(f"UIA路径: {uia_path}")
            logger.info(f"MSAA路径: {msaa_path}")

            hwnd = MSAAValidator.find_element_by_uia_path(ele, picker_type)
            logger.info(f"获取到的窗口句柄: {hwnd}")

            if hwnd == 0:
                logger.info("无法获取有效的窗口句柄")
                return False, "无法获取有效的窗口句柄", []

            ia_start_ele = MSAAValidator._get_msaa_ele_from_hwnd(hwnd)
            logger.info(f"获取到的IAccessible对象: {ia_start_ele}")

            if ia_start_ele is None:
                logger.info("无法获取IAccessible对象")
                return False, "无法获取IAccessible对象", []

            msaa_start_ele = MSAAElement(ia_start_ele, 0)
            logger.info(f'创建的MSAA元素: name="{msaa_start_ele.get_name()}", type="{msaa_start_ele.get_type()}"')

            elements = MSAAValidator.find_element_by_msaa_path(msaa_path, msaa_start_ele)
            logger.info(f"MSAA路径查找结果: {elements}")

            if elements and len(elements) > 0:
                logger.info("成功找到MSAA元素")
                return MSAALocator(elements[0])
            else:
                logger.info("未找到MSAA元素")
                return False, "未找到MSAA元素", []

        except Exception as e:
            logger.info(f"MSAA路径校验异常: {str(e)}")
            return False, f"路径校验异常: {str(e)}", []


class MSAAFactory:
    """MSAA工厂"""

    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs) -> Union[MSAALocator, None]:
        return MSAAValidator.validate(ele, picker_type)


msaa_factory = MSAAFactory()
