import dataclasses
import time
from copy import deepcopy
from typing import Any, List, Optional, Union

import pyautogui
from locator import ILocator, PickerType, Rect
from locator.utils.window import (
    find_window,
    find_window_by_enum,
    find_window_by_enum_list,
    find_window_handles_list,
    is_desktop_by_handle,
    show_desktop_rect,
    top_window,
    validate_window_rect,
)
from rpaframe.logger.logger import logger
from uiautomation import Control, ControlFromHandle


class UIALocator(ILocator):
    def __init__(self, control: Control):
        self.__control = control
        self.__rect = None

    def rect(self) -> Optional[Rect]:
        if self.__rect is None:
            rect = self.__control.BoundingRectangle
            logger.info(f"校验结果的初始rect {rect.left} {rect.top} {rect.right} {rect.bottom}")
            is_valid_rect = validate_window_rect(rect.left, rect.top, rect.right, rect.bottom)
            # logger.info(f'UIALocator rect  {is_valid_rect}')
            if not is_valid_rect:
                rect.left = 1 if rect.left < 0 else rect.left
                rect.top = 1 if rect.top < 0 else rect.top
                rect.right = pyautogui.size().width - 1 if rect.right > pyautogui.size().width else rect.right
                rect.bottom = pyautogui.size().height - 1 if rect.bottom > pyautogui.size().height else rect.bottom
            self.__rect = Rect(rect.left, rect.top, rect.right, rect.bottom)
        logger.info(f"校验结果的rect {self.__rect.to_json()}")
        return self.__rect

    def control(self) -> Any:
        return self.__control


@dataclasses.dataclass
class UIANode:
    """这个是前端PATH修改后的值，需要和UIAEle对比"""

    tag_name: str = None  # 标签名
    checked: bool = False  # 是否选中
    disable_keys: List[str] = None  # 禁用的key
    cls: str = None  # class name
    index: int = None  # 索引
    name: str = None
    value: str = None


class UIAEle:
    """这个是UIA的值，需要和前端PATH对比, 并记录对比结果"""

    def __init__(self, control: Control, index: int = None, index_match_sort: str = ""):
        # 上面是基于control，和index计算出来的数据
        self.__control = control
        self.__rect = None
        self.__index = index
        self.__cls = None
        self.__name = None
        self.__tag_name = None
        self.__value = None

        # 特殊: 这个是相对于UIANode的匹配数据, index的匹配不是强匹配
        self.index_parent_match_sort: str = ""
        self.index_match_sort: str = ""

    @property
    def rect(self):
        if self.__rect is None:
            bounding_rectangle = self.__control.BoundingRectangle
            self.__rect = Rect(
                bounding_rectangle.left,
                bounding_rectangle.top,
                bounding_rectangle.right,
                bounding_rectangle.bottom,
            )
        return self.__rect

    @property
    def tag_name(self):
        if self.__tag_name is None:
            self.__tag_name = self.__control.ControlTypeName
        return self.__tag_name

    @property
    def index(self):
        if self.__index is None:
            self.__index = 0
            pre = self.__control.GetPreviousSiblingControl()
            while pre:
                self.__index += 1
                pre = pre.GetPreviousSiblingControl()
        return self.__index

    @property
    def cls(self):
        if self.__cls is None:
            self.__cls = self.__control.ClassName
        return self.__cls

    @property
    def name(self):
        if self.__name is None:
            self.__name = self.__control.Name
        return self.__name

    @property
    def value(self):
        if self.__value is None:
            try:
                value = self.__control.GetValuePattern().Value  # noqa
            except Exception:  # noqa
                value = None
            self.__value = value
        return self.__value

    @property
    def control(self):
        return self.__control


class UIAFactory:
    """UIA工厂"""

    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs) -> Union[List[UIALocator], UIALocator, None]:
        if picker_type == PickerType.SIMILAR.value:
            return cls.__find_similar__(ele, picker_type, **kwargs)
        else:
            return cls.__find_one__(ele, picker_type, **kwargs)

    @classmethod
    def __get_child_walk_control__(cls, control: Control):
        child = control.GetFirstChildControl()
        index = 0
        while child:
            uia_ele = UIAEle(control=child, index=index)
            yield uia_ele
            index += 1
            child = child.GetNextSiblingControl()

    @classmethod
    def __compare_node_and_uia_ele__(cls, uia_ele: UIAEle, node: UIANode, keys: List[str]) -> bool:
        # 忽略没有选中
        if not node.checked:
            return True

        for key in keys:
            if key in node.disable_keys:
                continue
            v1 = getattr(node, key, None)
            v2 = getattr(uia_ele, key, None)
            if not v1 and not v2:
                continue
            if v1 != v2:
                return False
        return True

    @classmethod
    def __show_desktop_ele__(cls, root_handle, root_ctrl, rect):
        # 如果是桌面元素，将遮挡的窗口最小化
        if not root_handle or not root_ctrl:
            return
        if is_desktop_by_handle(root_handle, root_ctrl):
            show_desktop_rect(rect, desktop_handle=root_handle)
            time.sleep(0.2)

    @classmethod
    def _format_node_info(cls, node_or_obj) -> str:
        """格式化节点信息为单行字符串"""
        attrs = []
        for key in ["tag_name", "name", "cls", "value"]:
            value = getattr(node_or_obj, key, None)
            if value:  # 只显示有值的属性
                attrs.append(f"{key}={value}")
        return ", ".join(attrs)

    @classmethod
    def __find_similar__(cls, ele: dict, picker_type: str, **kwarg) -> Union[List[UIALocator], None]:
        path_list = ele.get("path", [])
        if not path_list:
            return None

        # 1. 先找到父路径
        parent_path = [v for v in path_list if v.get("similar_parent", False)]
        parent_ele = deepcopy(ele)
        parent_ele["path"] = parent_path
        parent_locator = cls.__find_one__(parent_ele, picker_type=picker_type, **kwarg)
        if not parent_locator:
            raise Exception("元素无法找到")
        assert isinstance(parent_locator.control(), Control)

        # 2. 再找子元素
        res = []
        node_list = [
            UIANode(
                tag_name=path.get("tag_name", None),
                checked=path.get("checked", None),
                disable_keys=path.get("disable_keys", []),
                cls=path.get("cls", None),
                index=path.get("index", None),
                name=path.get("name", None),
                value=path.get("value", None),
            )
            for path in path_list
            if not path.get("similar_parent", None)
        ]

        for root_ctrl in cls.__get_child_walk_control__(parent_locator.control()):
            # 判断第一场子元素是否符合规范
            root_ele = UIAEle(control=root_ctrl.control, index=0, index_match_sort="1")
            is_ok = cls.__compare_node_and_uia_ele__(root_ele, node_list[0], ["tag_name", "name", "cls", "value"])
            if not is_ok:
                continue

            if len(node_list) == 1:
                # 如果只有一层就直接结束
                res.append(UIALocator(control=root_ctrl.control))
                continue
            else:
                # 如果还有多层就需要向下遍历，并找到一个相近的值
                search_list = [UIAEle(control=root_ctrl.control, index=0, index_match_sort="1")]
                i = 0
                for i, node in enumerate(node_list[1:]):
                    # i 表示第几层

                    # 4.1 遍历查询里面的子集
                    child_list = []
                    for search in search_list:
                        for uia_ele in cls.__get_child_walk_control__(search.control):
                            uia_ele.index_parent_match_sort = search.index_match_sort
                            child_list.append(uia_ele)

                    # 4.2 基于前端传递的node, 过滤掉不符合要求的, 强匹配
                    child_list = [
                        item
                        for item in child_list
                        if cls.__compare_node_and_uia_ele__(item, node, ["tag_name", "name", "cls", "value"])
                    ]

                    # 4.3 基于前端传递的node, 处理index，弱匹配
                    for item in child_list:
                        index_match = cls.__compare_node_and_uia_ele__(item, node, ["index"])
                        item.index_match_sort = "{}{}".format(item.index_parent_match_sort, "1" if index_match else "0")

                    # 4.3 去一下层又去做比较，直到没有找人任何符合，或者层级结束
                    search_list = child_list
                    if not search_list:
                        break

                if not search_list or i != (len(node_list) - 2):
                    continue
                search_list.sort(key=lambda s: -int(s.index_match_sort))
                match = search_list[0]
                res.append(UIALocator(control=match.control))
        return res

    @classmethod
    def __find_one__(cls, ele: dict, picker_type: str, **kwargs) -> Union[UIALocator, None]:
        """
        使用列表遍历的方式查找窗口句柄，当找到元素时停止遍历
        使用 find_window_by_enum_list 和 find_window_handles_list 获取句柄列表
        """
        app_name = ele.get("app", "")
        path_list = ele.get("path", [])
        if not path_list:
            return None

        # 1. 处理前端path
        node_list = [
            UIANode(
                tag_name=path.get("tag_name", None),
                checked=path.get("checked", None),
                disable_keys=path.get("disable_keys", []),
                cls=path.get("cls", None),
                index=path.get("index", None),
                name=path.get("name", None),
                value=path.get("value", None),
            )
            for path in path_list
        ]

        first_cls = node_list[0].cls if node_list[0].cls not in node_list[0].disable_keys else None
        first_name = node_list[0].name if node_list[0].name not in node_list[0].disable_keys else None
        first_app_name = app_name if app_name not in node_list[0].disable_keys else None

        # 2. 获取所有可能的窗口句柄
        root_handles = []

        # 再尝试使用 find_window_handles_list 获取句柄列表
        try:
            handles_list = find_window_handles_list(
                first_cls, first_name, app_name=first_app_name, picker_type=picker_type
            )
            if handles_list:
                root_handles.extend(handles_list)
        except Exception as e:
            logger.debug(f"find_window_handles_list 调用失败: {e}")
        if len(root_handles) == 0:
            # 先尝试使用 find_window_by_enum_list 获取句柄列表
            try:
                enum_handles = find_window_by_enum_list(
                    first_cls,
                    first_name,
                    app_name=first_app_name,
                    picker_type=picker_type,
                )
                if enum_handles:
                    root_handles.extend(enum_handles)
            except Exception as e:
                logger.debug(f"find_window_by_enum_list 调用失败: {e}")

        # 去重处理
        root_handles = list(set(root_handles))

        if not root_handles:
            raise Exception("元素无法找到")

        logger.info(f"找到 {len(root_handles)} 个窗口句柄，开始遍历查找")

        # 3. 遍历所有句柄，尝试找到元素
        for idx, root_handle in enumerate(root_handles):
            try:
                logger.debug(f"正在尝试第 {idx + 1} 个句柄: {root_handle}")
                root_ctrl = ControlFromHandle(handle=root_handle)
                top_window(handle=root_handle, ctrl=root_ctrl)  # 置顶窗口

                # 4. 如果业务类型 WINDOW, 就直接结束
                if picker_type == PickerType.WINDOW.value:
                    logger.info(f"找到WINDOW类型元素，使用句柄: {root_handle}")
                    return UIALocator(control=root_ctrl)

                # 5. 忽略index的一层一层查找
                search_list = [UIAEle(control=root_ctrl, index=0, index_match_sort="1")]
                i = 0
                element_found = True  # 标记是否找到元素

                for i, node in enumerate(node_list[1:]):
                    # 5.1 遍历查询里面的子集
                    child_list = []
                    tag_list = []
                    for search in search_list:
                        for uia_ele in cls.__get_child_walk_control__(search.control):
                            uia_ele.index_parent_match_sort = search.index_match_sort
                            child_list.append(uia_ele)
                            tag_list.append(uia_ele.tag_name)

                    # logger.debug(f"拾取节点: {cls._format_node_info(node)}")
                    # for idx_child, ni in enumerate(child_list):
                    #     logger.debug(f"  节点{idx_child}: {cls._format_node_info(ni)}")

                    # 5.2 基于前端传递的node, 过滤掉不符合要求的, 强匹配
                    befor_cmp_child = child_list
                    child_list = [
                        item
                        for item in child_list
                        if cls.__compare_node_and_uia_ele__(item, node, ["tag_name", "name", "cls", "value"])
                    ]
                    # if len(child_list) > 0:
                    #     logger.info(f'筛选完是{child_list[0].tag_name}')

                    # 5.3 基于前端传递的node, 处理index，弱匹配
                    for item in child_list:
                        index_match = cls.__compare_node_and_uia_ele__(item, node, ["index"])
                        item.index_match_sort = "{}{}".format(item.index_parent_match_sort, "1" if index_match else "0")

                    # 5.4 去一下层又去做比较，直到没有找到任何符合，或者层级结束
                    search_list = child_list
                    if not search_list:
                        logger.debug(f"筛选完后剩余child_list为空 当前层级是{i} 候选taglist是 {tag_list}")
                        logger.debug(f"筛选前候选节点({len(befor_cmp_child)}个):")
                        for idx_child, ni in enumerate(befor_cmp_child):
                            logger.debug(f"  节点{idx_child}: {cls._format_node_info(ni)}")
                        logger.debug(f"拾取节点: {cls._format_node_info(node)}")
                        element_found = False
                        break

                # 6. 检查是否成功找到元素
                if element_found and search_list and i == (len(node_list) - 2):
                    # 7. 处理index
                    search_list.sort(key=lambda s: -int(s.index_match_sort))
                    match = search_list[0]

                    # 8. 后处理
                    # 显示桌面元素，遮挡的都隐藏掉
                    cls.__show_desktop_ele__(root_handle, root_ctrl, match.rect)
                    res = UIALocator(control=match.control)
                    logger.info(f"成功找到元素，使用句柄: {root_handle}，校验结果的rect {res.rect().to_json()}")
                    return res
                else:
                    logger.debug(f"句柄 {root_handle} 未找到匹配元素，继续尝试下一个")

            except Exception as e:
                # 如果当前句柄处理失败，继续尝试下一个句柄
                logger.debug(f"处理句柄 {root_handle} 时出错: {e}")
                continue

        # 如果所有句柄都无法找到元素，抛出异常
        logger.error(f"遍历了 {len(root_handles)} 个句柄，均未找到匹配元素")
        raise Exception("元素无法找到")

    @classmethod
    def __find_partial_match__(cls, ele: dict, picker_type: str, **kwargs) -> Union[UIALocator, None]:
        """
        根据路径查找元素，如果路径没有完全匹配，返回最后匹配的元素而不是报错
        """
        logger.info(f"UIAFactory __find_partial_match__ 开始查找元素 {ele}")
        app_name = ele.get("app", "")
        path_list = ele.get("path", [])
        if not path_list:
            return None

        # 1. 处理前端path
        node_list = [
            UIANode(
                tag_name=path.get("tag_name", None),
                checked=path.get("checked", None),
                disable_keys=path.get("disable_keys", []),
                cls=path.get("cls", None),
                index=path.get("index", None),
                name=path.get("name", None),
                value=path.get("value", None),
            )
            for path in path_list
        ]

        first_cls = node_list[0].cls if node_list[0].cls not in node_list[0].disable_keys else None
        first_name = node_list[0].name if node_list[0].name not in node_list[0].disable_keys else None
        first_app_name = app_name if app_name not in node_list[0].disable_keys else None

        # 2. 获取所有可能的窗口句柄
        root_handles = []

        # 再尝试使用 find_window_handles_list 获取句柄列表
        try:
            handles_list = find_window_handles_list(first_cls, first_name, app_name=first_app_name)
            if handles_list:
                root_handles.extend(handles_list)
        except Exception as e:
            logger.debug(f"find_window_handles_list 调用失败: {e}")
        if len(root_handles) == 0:
            # 先尝试使用 find_window_by_enum_list 获取句柄列表
            try:
                enum_handles = find_window_by_enum_list(first_cls, first_name, app_name=first_app_name)
                if enum_handles:
                    root_handles.extend(enum_handles)
            except Exception as e:
                logger.debug(f"find_window_by_enum_list 调用失败: {e}")

        # 去重处理
        root_handles = list(set(root_handles))

        if not root_handles:
            raise Exception("元素无法找到")

        logger.info(f"找到 {len(root_handles)} 个窗口句柄，开始遍历查找")

        # 3. 遍历所有句柄，尝试找到元素
        best_match = None
        best_match_depth = -1

        for idx, root_handle in enumerate(root_handles):
            try:
                logger.debug(f"正在尝试第 {idx + 1} 个句柄: {root_handle}")
                root_ctrl = ControlFromHandle(handle=root_handle)
                top_window(handle=root_handle, ctrl=root_ctrl)  # 置顶窗口

                # 5. 忽略index的一层一层查找
                search_list = [UIAEle(control=root_ctrl, index=0, index_match_sort="1")]
                # 根元素已经匹配了第一个节点，所以初始深度为1
                current_depth = 1
                last_valid_match = search_list[0]  # 根元素作为初始匹配

                for i, node in enumerate(node_list[1:]):
                    # 5.1 遍历查询里面的子集
                    child_list = []
                    tag_list = []
                    for search in search_list:
                        for uia_ele in cls.__get_child_walk_control__(search.control):
                            uia_ele.index_parent_match_sort = search.index_match_sort
                            child_list.append(uia_ele)
                            tag_list.append(uia_ele.tag_name)

                    # 5.2 基于前端传递的node, 过滤掉不符合要求的, 强匹配
                    befor_cmp_child = child_list
                    child_list = [
                        item
                        for item in child_list
                        if cls.__compare_node_and_uia_ele__(item, node, ["tag_name", "name", "cls", "value"])
                    ]

                    # 5.3 基于前端传递的node, 处理index，弱匹配
                    for item in child_list:
                        index_match = cls.__compare_node_and_uia_ele__(item, node, ["index"])
                        item.index_match_sort = "{}{}".format(item.index_parent_match_sort, "1" if index_match else "0")

                    # 5.4 如果找到了匹配的子元素，更新search_list和当前匹配深度
                    if child_list:
                        search_list = child_list
                        current_depth = i + 2  # i是从0开始的，加上根元素的1，所以是i+2
                        # 保存当前层级的最佳匹配
                        search_list.sort(key=lambda s: -int(s.index_match_sort))
                        last_valid_match = search_list[0]
                    else:
                        # 当前层级没有匹配，停止搜索
                        logger.debug(f"筛选完后剩余child_list为空 当前层级是{i} 候选taglist是 {tag_list}")
                        logger.debug(f"筛选前候选节点({len(befor_cmp_child)}个):")
                        for idx_child, ni in enumerate(befor_cmp_child):
                            logger.debug(f"  节点{idx_child}: {cls._format_node_info(ni)}")
                        logger.debug(f"拾取节点: {cls._format_node_info(node)}")
                        break

                # 6. 判断是否找到了更好的匹配
                if current_depth > best_match_depth:
                    best_match_depth = current_depth
                    if current_depth == len(node_list):
                        # 完全匹配，直接返回
                        cls.__show_desktop_ele__(root_handle, root_ctrl, last_valid_match.rect)
                        res = UIALocator(control=last_valid_match.control)
                        logger.info(f"完全匹配成功，使用句柄: {root_handle}，校验结果的rect {res.rect().to_json()}")
                        return res
                    else:
                        # 部分匹配，保存最佳匹配
                        best_match = (root_handle, root_ctrl, last_valid_match)
                        logger.debug(f"句柄 {root_handle} 部分匹配，深度: {current_depth}")

            except Exception as e:
                # 如果当前句柄处理失败，继续尝试下一个句柄
                logger.debug(f"处理句柄 {root_handle} 时出错: {e}")
                continue

        # 7. 返回最佳匹配结果
        if best_match:
            root_handle, root_ctrl, match_ele = best_match
            cls.__show_desktop_ele__(root_handle, root_ctrl, match_ele.rect)
            res = UIALocator(control=match_ele.control)
            logger.info(
                f"部分匹配成功，使用句柄: {root_handle}，匹配深度: {best_match_depth}，校验结果的rect {res.rect().to_json()}"
            )
            return res
        else:
            logger.error(f"遍历了 {len(root_handles)} 个句柄，均未找到任何匹配元素")
            raise Exception("元素无法找到")


uia_factory = UIAFactory()
