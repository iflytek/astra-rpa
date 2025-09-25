import json
from typing import Any, List, Optional, Union

import win32com.client
import win32con
import win32gui
import win32print
import win32process
from locator import ILocator, PickerType, Rect
from locator.utils.window import (
    find_window,
    get_screen_scale_rate_runtime,
    get_system_display_size,
    is_desktop_by_handle,
    show_desktop_rect,
    top_window,
    validate_ui_element_rect,
)
from rpaframe.logger.logger import logger
from uiautomation import Control, ControlFromHandle
from win32api import GetSystemMetrics


class SAPLocatorV2(ILocator):
    def __init__(
        self,
        rect,
        sap_context=None,
    ):
        self.sap_context = sap_context
        self.__rect = rect  # 缓存 rect

    def rect(self) -> Optional[Rect]:
        return self.__rect

    def control(self) -> Any:
        return self.sap_context


class SAPLocatorV1:
    """
    SAP元素定位1.0
    """

    def __init__(self, ele_data):
        self.ele_data = ele_data
        self.path = None
        self.sapguiauto = None
        self.application = None
        self.rect = Rect()

    def get_control_type(self, control):
        """获取控件类型并返回描述"""
        logger.info("get_control_type  start")
        try:
            # 获取类型字符串
            type_str = control.Type
            type_num = control.TypeAsNumber
            class_text = getattr(control, "Text").split(".")[1]
            logger.info(
                f"control{class_text} {control} control.Type {control.Type}  control.TypeAsNumber {control.TypeAsNumber}"
            )
            # 判断控件类型
            if "GridView" in class_text:
                return "GuiGridView"
            elif "TableTree" in class_text:
                return "GuiTree"
            else:
                return f"其他控件: {type_str} (类型号: {type_num})"

        except Exception as e:
            logger.info(f"错误: {str(e)}")

    def _init_sap_connection(self):
        """初始化SAP连接"""
        try:
            # from locator import sapguiauto, application
            sapguiauto = win32com.client.GetObject("SAPGUI")
            application = sapguiauto.GetScriptingEngine
            self.sapguiauto = sapguiauto  # win32com.client.GetObject("SAPGUI")
            self.application = application  # self.sapguiauto.GetScriptingEngine
            logger.info("locator SAP连接初始化成功")
        except Exception as e:
            logger.info(f"locator SAP连接初始化失败: {e}")
            self.sapguiauto = None
            self.application = None

    def get_screen_scale(self):
        def get_real_resolution():
            """获取真实的分辨率"""
            hDC = win32gui.GetDC(0)
            # 横向分辨率
            w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
            # 纵向分辨率
            h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
            return w, h

        def get_screen_size():
            """获取缩放后的分辨率"""
            w = GetSystemMetrics(0)
            h = GetSystemMetrics(1)
            return w, h

        real_resolution = get_real_resolution()
        screen_size = get_screen_size()

        screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)
        screen_scale_rate2 = get_screen_scale_rate_runtime()
        ratio = max(screen_scale_rate, screen_scale_rate2)
        logger.info(f"屏幕缩放比是1 {screen_scale_rate} 2 {screen_scale_rate2} res{ratio}")
        return ratio

    def get_ctrl_by_id(self, ctrl_id):
        conn = self.application.Children(0)
        session = conn.Children(0)
        ctrl = session.findById(ctrl_id, False)
        return ctrl

    def get_cell_nodes_by_ctrl_from_point(self, ctrl, row, col_name):
        try:
            container_left = ctrl.ScreenLeft
            container_top = ctrl.ScreenTop
            logger.info(f"get_cell_nodes_by_ctrl_from_point container {container_left}  {container_top}")
            # 获取单元格位置信息（相对于控件）
            cell_left = ctrl.GetCellLeft(row, col_name)
            cell_top = ctrl.GetCellTop(row, col_name)
            cell_width = ctrl.GetCellWidth(row, col_name)
            cell_height = ctrl.GetCellHeight(row, col_name)

            # 计算屏幕绝对坐标
            abs_left = cell_left + container_left
            abs_top = cell_top + container_top
            return {
                "height": cell_height,
                "left": abs_left,
                "top": abs_top,
                "width": cell_width,
            }
        except Exception as e:
            logger.info(e)
            return {"height": 0, "left": 0, "top": 0, "width": 0}

    def get_tree_nodes_by_ctrl_from_point(self, ctrl, text):
        """
        获取树形控件中位于指定坐标点(x,y)的最小矩形节点
        优先返回不加偏移坐标命中的最小组件，否则返回加偏移坐标命中的最小组件

        Args:
            x: 屏幕坐标X
            y: 屏幕坐标Y
            ctrl: 树形控件对象
            ctrl_id: 控件ID

        Returns:
            包含节点信息的字典（如果找到），否则返回None
        """
        container_left = ctrl.ScreenLeft
        container_top = ctrl.ScreenTop
        tree_ctrl = ctrl
        if not tree_ctrl:
            logger.info(f"未找到控件: {ctrl}")
            return None

        try:
            node_keys = tree_ctrl.GetAllNodeKeys()
            if not hasattr(node_keys, "Count"):
                logger.info("无法获取节点键值列表")
                return None

            logger.info("开始遍历树形节点")
            for i in range(node_keys.Count):
                try:
                    key = node_keys.Item(i)
                    # 获取节点位置信息
                    node_text = tree_ctrl.GetItemText(key, 1)

                    # 检查不加偏移的坐标匹配
                    if node_text == text:
                        logger.info("找到直接坐标匹配的节点")
                        node_left = tree_ctrl.GetItemLeft(key, 1) + container_left
                        node_top = tree_ctrl.GetItemTop(key, 1) + container_top
                        node_width = tree_ctrl.GetItemWidth(key, 1)
                        node_height = tree_ctrl.GetItemHeight(key, 1)

                except Exception as e:
                    logger.error(f"处理节点 {i} 时出错: {str(e)}")
                    continue

            return {
                "height": node_height,
                "left": node_left,
                "top": node_top,
                "width": node_width,
            }
        except Exception as e:
            logger.error(f"遍历节点时出错: {str(e)}")
            return {"height": 0, "left": 0, "top": 0, "width": 0}

    def getElementRect(self, ctrl, type_str, path_dic):
        """
        根据ctrl类型
        """

        res = {"height": 0, "left": 0, "top": 0, "width": 0}
        text = path_dic.get("text", None)
        row = path_dic.get("row", None)
        colName = path_dic.get("colName", None)
        if not text and not row and not colName:
            left = ctrl.ScreenLeft
            top = ctrl.ScreenTop
            width = ctrl.Width
            height = ctrl.Height
            return {"height": height, "left": left, "top": top, "width": width}
        else:
            if type_str == "GuiTree":
                logger.info("该控件是树形控件，获取节点信息...")
                res = self.get_tree_nodes_by_ctrl_from_point(ctrl, text)
                logger.info(f"节点信息获取成功{res}")
            elif type_str == "GuiGridView":
                logger.info("该控件是GuiGridView控件，获取节点信息...")
                res = self.get_cell_nodes_by_ctrl_from_point(ctrl, row, colName)
                logger.info(f"节点信息获取成功{res}")

        return res

    def scroll_ele(self, ctrl):
        pass

    def validate(self):
        app = self.ele_data["app"]
        path = self.ele_data["path"]  # self.customized_path(self.ele_data["path"])
        handle = find_window(path[0]["cls"], path[0]["name"], app_name=app)
        logger.info(f"校验的第一层信息 {path[0]['cls']} {path[0]['name']}  {app}")
        # 应该用uia让他置顶
        if not handle:
            raise Exception("元素无法找到")
        _, pid = win32process.GetWindowThreadProcessId(handle)
        print("pid是{}".format(pid))
        # 将路径变成字符串去找目标
        if not path or len(path) < 1:
            raise Exception("请勾选校验信息")
        if len(path) == 1:
            ###使用uia的校验
            from .uia_locator import UiaLocatorV1

            return UiaLocatorV1(self.ele_data)

        root_control: Control = ControlFromHandle(handle)
        top_window(handle, root_control)

        ratio = self.get_screen_scale()

        ctrl_id = path[1]["id"]
        # text=None if len(path[1])<2 else path[1].get("text",None)

        self._init_sap_connection()  #

        # 设置self.rect
        ctrl = self.get_ctrl_by_id(ctrl_id)  # 校验失败也可能是字符串在c++中被截断

        type_str = self.get_control_type(ctrl)
        logger.info(f"get_control_type type_str {type_str}")

        # 滚动到可视区域,目前未完成，因为缺少可验证场景以及sap功能支持调研
        self.scroll_ele(ctrl)

        rect_wywh = self.getElementRect(ctrl, type_str, path[1])
        rect_wywh["left"] = rect_wywh["left"]
        rect_wywh["top"] = rect_wywh["top"]
        logger.info(f"校验路径获取的rect信息 {rect_wywh} 缩放比是{ratio}")

        left = rect_wywh["left"] if rect_wywh["left"] >= 0 else 0
        top = rect_wywh["top"] if rect_wywh["top"] >= 0 else 0
        right = rect_wywh["left"] + rect_wywh["width"] if rect_wywh["left"] + rect_wywh["width"] >= 0 else 0
        bottom = rect_wywh["top"] + rect_wywh["height"] if rect_wywh["top"] + rect_wywh["height"] >= 0 else 0
        right = right if right >= left else left
        bottom = bottom if bottom >= top else top

        display = get_system_display_size()
        max_value_screen = [int(ratio * display[0]), int(ratio * display[1])]
        if not validate_ui_element_rect(left, top, right, bottom, max_value_screen[0], max_value_screen[1]):
            logger.info("current rect is Invalid")
            left = 0
            top = 0
            right = 1
            bottom = 1

        self.rect = Rect(int(left), int(top), int(right), int(bottom))
        logger.info(f"the final rect of validate {self.rect}")
        return SAPLocatorV2(rect=self.rect, sap_context=path[1])

    def __getattr__(self, item):
        if isinstance(self.ele_data, str):
            self.ele_data = json.loads(self.ele_data)
        return self.ele_data[item]


class SAPFactory:
    """SAP工厂"""

    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs):
        return SAPLocatorV1(ele_data=ele).validate()


sap_factory = SAPFactory()
