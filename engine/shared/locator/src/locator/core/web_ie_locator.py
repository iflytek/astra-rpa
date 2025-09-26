import json
import traceback
from typing import Any, Optional, Union

import uiautomation as auto
from rpaframe.logger.logger import logger

from locator import BrowserType, Rect, like_chrome_browser_type
from locator.core.web_ie_locator_dll import *
from locator.core.web_locator import WEBLocator
from locator.utils.window import top_window


class WEBIELocator(WEBLocator):
    def __init__(self, rect=None, rects=None):
        super().__init__(rect, rects)
        self.__rect = rect
        self.__rects = rects

    def rect(self) -> Optional[Rect]:
        if self.__rects is not None and len(self.__rects) > 0:
            return self.__rects
        return self.__rect

    def control(self) -> Any:
        return None


class WebIEFactory:
    """WebIE工厂"""

    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs) -> Union[list[WEBIELocator], WEBIELocator, None]:
        if ele.get("app", "") in like_chrome_browser_type:
            # 直接结束
            return None

        scroll_into_view = "true" if kwargs.get("scroll_into_view", True) else "false"  # 开启是否滚动

        # 获取元素配置
        path = ele.get("path", {})
        iframe_index = path.get("iframeIndex", None)
        check_type = path.get("checkType", None)  # 选择类型，是使用可视化还是自定义
        match_types = path.get("matchTypes", "")  # 选择匹配方式，是匹配位置，滚动加载
        scroll_into_view_time = "false" if "scrollPosition" in match_types else "true"  # 开启是否滚动若干次

        css_selector = path.get("cssSelector", None)
        path_dirs = path.get("pathDirs", [])
        xpath = path.get("xpath", "")

        try:
            if "similarCount" in path:
                if check_type == "customization":
                    res = cls.__ele_css_selector_handler__(
                        css_selector, iframe_index, scroll_into_view=scroll_into_view
                    )
                else:
                    res = cls.__ele_path_dirs_handler__(
                        path_dirs,
                        iframe_index,
                        scroll_into_view=scroll_into_view,
                        scroll_into_view_time=scroll_into_view_time,
                    )
                res = eval(res)
                rect = Rect(
                    int(float(res[0]["left"])),
                    int(float(res[0]["top"])),
                    int(float(res[0]["left"])) + int(float(res[0]["w"])),
                    int(float(res[0]["top"])) + int(float(res[0]["h"])),
                )
                rects = []
                if len(res) > 1:
                    for s_rect in res:
                        rects.append(
                            Rect(
                                int(float(s_rect["left"])),
                                int(float(s_rect["top"])),
                                int(float(s_rect["left"])) + int(float(s_rect["w"])),
                                int(float(s_rect["top"])) + int(float(s_rect["h"])),
                            )
                        )
                return WEBIELocator(rect=rect, rects=rects)
            else:
                if check_type == "customization":
                    if "onlyPosition" in match_types:
                        if not cls.__check_xpath__(xpath_str=xpath):
                            raise Exception("xpath无效")
                        logger.info("走的 __ele_xpath_handler__  xpath: {}".format(xpath))
                        res = cls.__ele_xpath_handler__(xpath, iframe_index)
                        rect = Rect(
                            int(float(res["left"])),
                            int(float(res["top"])),
                            int(float(res["left"])) + int(float(res["w"])),
                            int(float(res["top"])) + int(float(res["h"])),
                        )
                    else:
                        res = cls.locate_ele_by_direct_css_selector(
                            css_selector,
                            iframe_index,
                            scroll_into_view=scroll_into_view,
                        )
                        res = eval(res)
                        rect = Rect(
                            int(float(res[0]["left"])),
                            int(float(res[0]["top"])),
                            int(float(res[0]["left"])) + int(float(res[0]["w"])),
                            int(float(res[0]["top"])) + int(float(res[0]["h"])),
                        )
                    return WEBIELocator(rect=rect)
                else:
                    if all(not node.get("checked", True) for node in path_dirs):
                        raise Exception("请选中至少一项校验所需参考信息")
                    if "onlyPosition" in match_types:
                        path_dirs_only_index = cls.__modify_pathdir_attributes__(path_dirs)
                        res = cls.__ele_path_dirs_handler__(
                            path_dirs_only_index,
                            iframe_index,
                            scroll_into_view=scroll_into_view,
                            scroll_into_view_time=scroll_into_view_time,
                        )
                    else:
                        res = cls.__ele_path_dirs_handler__(
                            path_dirs,
                            iframe_index,
                            scroll_into_view=scroll_into_view,
                            scroll_into_view_time=scroll_into_view_time,
                        )
                    res = eval(res)
                    rect = Rect(
                        int(float(res[0]["left"])),
                        int(float(res[0]["top"])),
                        int(float(res[0]["left"])) + int(float(res[0]["w"])),
                        int(float(res[0]["top"])) + int(float(res[0]["h"])),
                    )
                    rects = []
                    if len(res) > 1:
                        for s_rect in res:
                            rects.append(
                                Rect(
                                    int(float(s_rect["left"])),
                                    int(float(s_rect["top"])),
                                    int(float(s_rect["left"])) + int(float(s_rect["w"])),
                                    int(float(s_rect["top"])) + int(float(s_rect["h"])),
                                )
                            )
                    return WEBIELocator(rect=rect, rects=rects)
        except Exception as e:
            logger.error("find error: {}".format(e))
            logger.error("堆栈信息:\n{}".format(traceback.format_exc()))
            raise Exception("元素查找失败，请勾选可视化信息或者使用自定义")

    @classmethod
    def locate_ele_by_direct_css_selector(cls, cssSelector, iframeIndex, scroll_into_view, scrollPosition="false"):
        ie_win = auto.WindowControl(searchDepth=1, ClassName="IEFrame")
        ie_doc = ie_win.PaneControl(ClassName="Internet Explorer_Server")
        hwnd = ie_doc.NativeWindowHandle
        page_info = IEAutomationClass().getBoudingOfContainer(hwnd, "", int(iframeIndex), "")
        screen_top = page_info["top"]
        screen_left = page_info["left"]
        ieRatio = page_info["ieRatio"]
        scroll_into_view_tag = scroll_into_view

        script = (
            f"""
                        // 根据属性名获得对应属性值
                        function getAttr(element, regAttr) {{
                            if (regAttr.name == "innerText") {{
                                return element.innerText;
                            }}

                            var attrs = [];
                            for (var i = 0; i < element.attributes.length; i++) {{
                                var attr = element.attributes[i];
                                if (attr.name === regAttr.name) {{
                                    return attr.value
                                }}
                            }}
                            return attrs;
                        }}


                        var SCROLL_TIMES=20;
                        var SCROLL_DELAY=1500;
                        /**
                            * 滚动查找元素，如果找不到，则滚动查找
                            * 最多滚动20次当前窗口高度
                            * SCROLL_TIMES = 20 最大滚动次数
                            * SCROLL_DELAY = 1500ms // 单次滚动后等待页面加载的时间
                        */
                        function scrollFindElement(cssSelector) {{
                            var windowHeight = window.innerHeight;  // 获取窗口的高度
                            var windowScrollTop = document.documentElement.scrollTop || document.body.scrollTop;  // 获取当前滚动的高度
                            console.log('windowScrollTop: ', windowScrollTop);
                            console.log('windowHeight: ', windowHeight);
                            console.log('SCROLL_TIMES: ', SCROLL_TIMES);
                            var count = 1;

                            var totalMatchedElements = [];  // 用于存储所有匹配的元素

                            function callback() {{
                                const rects = [];
                                if (totalMatchedElements.length > 0 && {scroll_into_view_tag})
                                    totalMatchedElements[Math.floor((totalMatchedElements.length - 1) / 2)].scrollIntoView(false);
                                // 得到元素位置信息
                                totalMatchedElements.forEach(function(element) {{
                                    left = element.getBoundingClientRect().left + {screen_left};
                                    top_tmp = element.getBoundingClientRect().top + {screen_top};
                                    _left = left * {ieRatio};
                                    _top = top_tmp * {ieRatio};
                                    _width = element.getBoundingClientRect().width * {ieRatio};
                                    _height = element.getBoundingClientRect().height * {ieRatio};
                                    rects.push({{
                                        left: _left,
                                        top: _top,
                                        w: _width,
                                        h: _height,
                                    }});
                                }});
                                var hiddenInput = document.getElementById('iflyrpa123');
                                if (!hiddenInput) {{
                                    hiddenInput = document.createElement('input');
                                    hiddenInput.type = 'hidden';
                                    hiddenInput.id = 'iflyrpa123';
                                    document.body.appendChild(hiddenInput);
                                }}
                                hiddenInput.setAttribute('match_ele',JSON.stringify(rects)) ;
                                hiddenInput.setAttribute('iflyrpaKeys','match_ele');         
                            }}


                            // 初始查找元素
                            function findAndCheckElements() {{
                                var result = document.querySelectorAll(cssSelector);
                                console.log('待匹配的元素:', result);
                                let element_arr = [];
                                for(var i =0;i < result.length;i++){{
                                    element_arr.push(result[i]);
                                }}
                                totalMatchedElements=element_arr;
                            }}

                            // 查找元素
                            findAndCheckElements();
                            if (totalMatchedElements.length > 0) {{
                                callback();
                                return;
                            }}
                            if( {scrollPosition}){{
                                return ;
                            }}

                            // 如果已经滚动到最大目标位置，直接获取元素
                            if (windowScrollTop < SCROLL_TIMES * windowHeight) {{
                                // 否则开始滚动查找
                                console.log('开始滚动');
                                scrollFn();
                            }} else {{
                                callback();
                                return;
                            }}



                            // 滚动查找函数
                            function scrollFn() {{
                                console.log('count: ', count);
                                window.scrollTo(window.scrollX, count * windowHeight);  // 滚动到指定位置

                                // 开始滚动查找
                                // 使用 setTimeout 来模拟延时等待页面加载
                                setTimeout(function () {{
                                    findAndCheckElements();  // 查找元素并校验
                                    if (totalMatchedElements.length > 0) {{
                                        callback();
                                        return;
                                    }}
                                    if (count < SCROLL_TIMES) {{ // 滚动次数小于最大滚动次数，继续滚动查找
                                        count++;
                                        scrollFn();  // 递归调用
                                    }} else {{ // 滚动次数达到最大滚动次数，返回匹配的元素
                                            console.log('达到最大滚动次数，返回匹配的元素');
                                            callback();
                                    }}
                                }}, SCROLL_DELAY); // 等待页面加载
                            }}
                        }}

                        function findElementBySelector(selector) {{
                            scrollFindElement(selector)
                        }}



                        """.replace("{", "{{").replace("}", "}}")
            + """findElementBySelector(" """
            + cssSelector
            + ' " '
            + ")"
        )

        # script = script.replace('{', '{{')
        # script = script.replace('}', '}}')
        res = IEAutomationClass().executeJsScroll(hwnd, script, int(iframeIndex), "wait use")["match_ele"]
        return res

    @classmethod
    def __ele_xpath_handler__(cls, xpath, iframeIndex):
        ie_win = auto.WindowControl(searchDepth=1, ClassName="IEFrame")
        ie_doc = ie_win.PaneControl(ClassName="Internet Explorer_Server")
        hwnd = ie_doc.NativeWindowHandle
        script = (
            "setInputValueByXPath('"
            + xpath
            + "');"
            + r"""
            function startsWithRpa(strT,str){{
               if(str==null||str==''||strT.length==0||str.length>strT.length){{
               return false;

               }}

               if(strT.substr(0,str.length)==str){{
               return true;

               }}else{{
               return false;

               }}
           }}
           function setInputValueByXPath(xpath) {{
            function findElementByXPath(xpath) {{
                // Regular expression to match parts of XPath
                var pathRegex = /\/{{1,2}}[^\/]+/g;
                var parts = xpath.match(pathRegex);
                if (!parts || parts.length === 0) {{
                    console.error('Invalid XPath:', xpath);
                    return null;
                }}

                var root = document; // Start from the current document

                // Helper function to find element recursively
                function findElement(node, pathParts) {{
                    if (pathParts.length === 0) {{
                        return null;
                    }}

                    var part = pathParts.shift().trim();

                    if (part === '') {{
                        return findElement(node, pathParts); // Skip empty parts
                    }}

                    var isRelative = startsWithRpa(part,'//');
                    var tagName=null ;
                    var index=0;
                    var attribute = null;
                    var value = null;
                    if (isRelative) {{
                        part = part.substr(2).trim();
                        // Match for tag name, index, and attribute conditions
                        var match = part.match(/^(\w+)(?:\[@(\w+)(?:=""([^""]+)"")?\])?$/);

                        if (!match) {{
                            console.error('XPath part parsing error:', part);
                            return null;
                        }}

                        if (match.length === 4) {{
                            if (match[0].indexOf('@') != -1) {{
                                attribute = match[2];
                                value = match[3];
                            }} else {{
                                tagName = match[1].toUpperCase();
                            }}
                        }}
                    }} else {{
                        part = part.substr(1).trim(); // Remove leading slash for absolute paths
                        var match = part.match(/^(\w+)(?:\[(\d+)\])?$/);
                        if (!match) {{
                            console.error('XPath 部分解析错误:', part);
                            return null;
                        }}
                        tagName = match[1].toUpperCase();
                        index = match[2] ? parseInt(match[2], 10) - 1 : 0; // Convert XPath index to DOM index
                    }}

                    if(!isRelative){{
                        var currentNode = node.firstChild;
                        var foundIndex = -1;
                        while (currentNode) {{
                            if (currentNode.nodeType === 1 && currentNode.tagName === tagName) {{
                                foundIndex++;
                                if (foundIndex === index) {{
                                    break;
                                }}
                            }}
                            currentNode = currentNode.nextSibling;
                        }}
                    }}else{{//如果是相对路径，找当前的节点
                        console.log(attribute);
                        console.log(value);
                        if (attribute !== null && value !== null) {{
                            if (attribute === 'id') {{
                                // Find element by ID
                                currentNode = node.getElementById(value);
                            }} else if (attribute === 'class') {{
                                // Find elements by class name
                                currentNode = node.getElementsByClassName(value)[0];
                            }} else {{
                                console.error('Unsupported attribute:', attribute);
                                return null;
                            }}
                        }} else {{
                            // Find elements by tag name
                            currentNode = node.getElementsByTagName(tagName)[0];
                        }}
                    }}

                    if (!currentNode) {{
                        console.error('索引超出范围:', tagName, index);
                        return null;
                    }}
                    if (currentNode.tagName === 'IFRAME') {{
                        console.log('找到 iframe:', currentNode);
                        var iframeDoc = currentNode.contentDocument || currentNode.contentWindow.document;
                        console.log('进入 iframe 文档:', iframeDoc);
                        var tmpNode=findElement(iframeDoc, pathParts);
                        return tmpNode==null?currentNode:tmpNode;
                    }}

                    if (pathParts.length === 0) {{
                        return currentNode;
                    }}

                    var tmpFindNode=findElement(currentNode, pathParts);
                    return tmpFindNode==null?currentNode:tmpFindNode;
                }}

                return findElement(root, parts.slice()); 
                }}



                   var element = findElementByXPath(xpath);
                   if(element){{
                        element.scrollIntoView(false)
                   }}

                   var hiddenInput = document.getElementById('iflyrpa123');
        if (!hiddenInput) {{
            hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.id = 'iflyrpa123';
            document.body.appendChild(hiddenInput);
        }}
        hiddenInput.setAttribute('left',element.getBoundingClientRect().left) ;
        hiddenInput.setAttribute('top',element.getBoundingClientRect().top) ;
        hiddenInput.setAttribute('w',element.getBoundingClientRect().width) ;
        hiddenInput.setAttribute('h',element.getBoundingClientRect().height);
        hiddenInput.setAttribute('innerText',element.innerText);
        hiddenInput.setAttribute('iflyrpaKeys','left-top-w-h-innerText');
                                                       }}
                """
        )  # 根据绝对xpath定位元素，将元素信息插入input
        res = IEAutomationClass().executeJsGetBouding(hwnd, script, int(iframeIndex), "")
        return res

    @classmethod
    def __ele_css_selector_handler__(cls, css_selector, iframeIndex, scroll_into_view="true"):
        ie_win = auto.WindowControl(searchDepth=1, ClassName="IEFrame")
        ie_doc = ie_win.PaneControl(ClassName="Internet Explorer_Server")
        hwnd = ie_doc.NativeWindowHandle
        page_info = IEAutomationClass().getBoudingOfContainer(hwnd, "", int(iframeIndex), "")
        screen_top = page_info["top"]
        screen_left = page_info["left"]
        ie_ratio = page_info["ieRatio"]
        script = (
            f"""
            function findSimilarElementBySelector(selector) {{
                var result = document.querySelectorAll(selector);
                let element_arr = [];
                for(var i =0;i < result.length;i++){{
                    element_arr.push(result[i]);
                }}

                const rects = [];
                if (element_arr.length > 0) {{
                    if({scroll_into_view}){{
                        element_arr[Math.floor((element_arr.length - 1) / 2)].scrollIntoView(false);
                    }}

                    // 得到元素位置信息
                    element_arr.forEach(function(element) {{
                        left = element.getBoundingClientRect().left + {screen_left};
                        top_tmp = element.getBoundingClientRect().top + {screen_top};
                        _left = left * {ie_ratio};
                        _top = top_tmp * {ie_ratio};
                        _width = element.getBoundingClientRect().width * {ie_ratio};
                        _height = element.getBoundingClientRect().height * {ie_ratio};
                        rects.push({{
                            left: _left,
                            top: _top,
                            w: _width,
                            h: _height,
                        }});
                    }});
                    var hiddenInput = document.getElementById('iflyrpa123');
                    if (!hiddenInput) {{
                        hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.id = 'iflyrpa123';
                        document.body.appendChild(hiddenInput);
                    }}
                    hiddenInput.setAttribute('match_ele',JSON.stringify(rects)) ;
                    hiddenInput.setAttribute('iflyrpaKeys','match_ele');
                }}
            }}
        """.replace("{", "{{").replace("}", "}}")
            + """findSimilarElementBySelector('"""
            + css_selector
            + "')"
        )
        res = IEAutomationClass().executeJs(hwnd, script, int(iframeIndex), "wait use")["match_ele"]
        return res

    @classmethod
    def __ele_path_dirs_handler__(
        cls,
        pathdirs,
        iframeIndex,
        scroll_into_view="true",
        scroll_into_view_time="false",
    ):
        ie_win = auto.WindowControl(searchDepth=1, ClassName="IEFrame")
        ie_doc = ie_win.PaneControl(ClassName="Internet Explorer_Server")
        hwnd = ie_doc.NativeWindowHandle
        page_info = IEAutomationClass().getBoudingOfContainer(hwnd, "", int(iframeIndex), "")
        screen_top = page_info["top"]
        screen_left = page_info["left"]
        ie_ratio = page_info["ieRatio"]
        # 对pathdirs进行预处理，清理可能导致JS语法错误的字符
        script = (
            f"""
                     /**
                     * 元素查找与验证工具 - IE兼容版
                     * 基于pathdirs信息构建选择器并查找筛选元素
                     */

                    // 配置参数
                    var SCROLL_TIMES = 20;     // 最大滚动次数
                    var SCROLL_DELAY = 1500;   // 单次滚动等待时间(ms)

                    /**
                     * 根据属性名获取元素属性值
                     */
                    function getAttr(element, regAttr,is_blanck) {{
                        is_blanck = typeof is_blanck === 'undefined' ? 0 : is_blanck;
                        // 特殊处理innerText
                        if (regAttr.name === "innerText") {{
                            return element.innerText;
                        }}

                        // 处理特殊属性
                        if (regAttr.name === "@index") {{
                            // 获取元素在所有兄弟元素中的索引
                            var parent = element.parentElement;
                            if (!parent) return "1";

                            var siblings = parent.children;
                            for (var i = 0; i < siblings.length; i++) {{
                                if (siblings[i] === element) {{
                                    return String(i+1);
                                }}
                            }}
                            return "-1";
                        }}

                        // 查找匹配的常规属性
                        for (var j = 0; j < element.attributes.length; j++) {{
                            var attr = element.attributes[j];
                            if (attr.name === regAttr.name) {{
                                var value = attr.value;
                                if (attr.name === 'class' && is_blanck==1) {{
                                    // 去除无意义字符，多个空白字符（包括换行、制表、全角空格等）都替换为一个半角空格   跟拾取一样，因为ie中元素获取的值有时候是不一样的，跟edge表现不一样
                                    value = value.replace(/[\\r\\n\\t\\f\\v\\u00A0\\u1680\\u2000-\\u200A\\u202F\\u205F\\u3000]+/g, ' ') // 替换所有不可见空白字符
                                                .replace(/\\s+/g, ' ') // 再次替换多个空白为单个空格
                                                .trim();
                                }}
                                return value;
                            }}
                        }}

                        return [];
                    }}

                    /**
                     * 从pathdirs构建CSS选择器
                     */
                    function buildSelectorFromPathdir(pathdirs) {{
                        var selector = "";
                        var firstCheckedElem = null;

                        // 找到第一个checked为true的元素
                        for (var i = 0; i < pathdirs.length; i++) {{
                            if (pathdirs[i].checked === true) {{
                                firstCheckedElem = pathdirs[i];
                                break;
                            }}
                        }}

                        if (!firstCheckedElem) {{
                            return ""; // 如果没有checked的元素，返回通配符
                        }}

                        // 构建选择器
                        selector = firstCheckedElem.tag ;

                        // 添加完全匹配且checked为true的属性
                        for (var j = 0; j < firstCheckedElem.attrs.length; j++) {{
                            var attr = firstCheckedElem.attrs[j];
                            if (attr.checked === true && attr.type === 0 && attr.name !== "innerText") {{
                                if (attr.name === "class") {{
                                    // 类名需要特殊处理，因为可能有多个类
                                    var classes = attr.value.split(/\\s+/);
                                    for (var k = 0; k < classes.length; k++) {{
                                        if (classes[k]) {{
                                            selector += "." + classes[k];
                                        }}
                                    }}
                                }} else if (attr.name === "id") {{
                                    var value = attr.value;
                                    var isNumeric = !isNaN(parseFloat(value)) && isFinite(value) && value.toString().trim() !== "";
                                    if (!isNumeric) {{
                                        selector += "#" + attr.value;
                                    }}
                                }}else if (attr.name === "@index" ) {{
                                    if(firstCheckedElem.tag !== 'html'){{
                                        indexValue = parseInt(attr.value, 10);
                                        selector += ":nth-of-type(" + indexValue + ")";
                                    }}
                                 }}
                                 else {{
                                    selector += "[" + attr.name + "=\\"" + attr.value + "\\"]";
                                }}
                            }}
                        }}

                        return selector;
                    }}

                    /**
                     * 检查元素是否符合特定属性条件
                     */
                    function checkElementAttributes(element, pathdirItem) {{
                        var attrs = pathdirItem.attrs;

                        // 检查每个选中的属性
                        for (var i = 0; i < attrs.length; i++) {{
                            var attr = attrs[i];
                            if (!attr.checked) continue;  // 跳过未选中的属性

                            var nodeValue = String(attr.value);

                            var value = getAttr(element, attr);

                            // 根据不同类型进行匹配
                            if (attr.type === 0) {{           // 完全匹配
                                if (value !== nodeValue && nodeValue!==getAttr(element, attr,1)) {{
                                    return false;
                                }}
                            }} else if (attr.type === 1) {{    // 通配符匹配
                                var wildcardPattern = nodeValue.replace(/\\?/g, ".").replace(/\\*/g, ".*");
                                var reg = new RegExp('^' + wildcardPattern + '$');
                                if (!reg.test(value)) {{
                                    return false;
                                }}
                            }} else if (attr.type === 2) {{    // 正则匹配
                                var reg = new RegExp(nodeValue);
                                if (!reg.test(value)) {{
                                    return false;
                                }}
                            }}
                        }}

                        return true;
                    }}

                    /**
                     * 递归检查元素及其子元素是否符合路径规则
                     */
                    function findMatchingElements(element, pathdirs, index) {{
                        if (index >= pathdirs.length) {{
                            return [element];
                        }}

                        var currentPathdir = pathdirs[index];
                        var results = [];

                        // 如果当前路径节点未被选中，直接跳到下一个
                        if (currentPathdir.checked === false) {{
                            return findMatchingElements(element, pathdirs, index + 1);
                        }}

                        // 如果是第一个节点，已经使用选择器查找过，只需验证其他属性
                        if (index === 0) {{


                            if (checkElementAttributes(element, currentPathdir)) {{

                                var childResults = findMatchingElements(element, pathdirs, index + 1);
                                for (var i = 0; i < childResults.length; i++) {{
                                    results.push(childResults[i]);
                                }}
                            }}
                            return results;
                        }}

                        // 获取所有子元素
                        var children = element.children;
                        for (var j = 0; j < children.length; j++) {{
                            var child = children[j];

                            // 检查标签名是否匹配
                            if (currentPathdir.tag && child.tagName.toLowerCase() !== currentPathdir.tag.toLowerCase()) {{
                                continue;
                            }}

                            // 检查属性
                            if (checkElementAttributes(child, currentPathdir)) {{
                                var nextResults = findMatchingElements(child, pathdirs, index + 1);
                                for (var k = 0; k < nextResults.length; k++) {{
                                    results.push(nextResults[k]);
                                }}
                            }}
                        }}

                        return results;
                    }}

                    /**
                     * 处理匹配到的元素
                     */
                    function handleMatchedElements(matchedElements) {{
                        var rects = [];

                        // 滚动到匹配元素中间位置
                        if (matchedElements.length > 0 && {scroll_into_view}) {{
                            var middleIndex = Math.floor((matchedElements.length - 1) / 2);
                            matchedElements[middleIndex].scrollIntoView(false);
                        }}

                        // 获取所有匹配元素的位置信息
                        for (var i = 0; i < matchedElements.length; i++) {{
                            var element = matchedElements[i];
                            var boundingRect = element.getBoundingClientRect();
                            var left = boundingRect.left + {screen_left};
                            var top = boundingRect.top + {screen_top};

                            rects.push({{
                                left: left * {ie_ratio},
                                top: top * {ie_ratio},
                                w: boundingRect.width * {ie_ratio},
                                h: boundingRect.height * {ie_ratio}
                            }});
                        }}

                        // 存储结果到隐藏input元素
                        var hiddenInput = document.getElementById('iflyrpa123');
                        if (!hiddenInput) {{
                            hiddenInput = document.createElement('input');
                            hiddenInput.type = 'hidden';
                            hiddenInput.id = 'iflyrpa123';
                            document.body.appendChild(hiddenInput);
                        }}

                        hiddenInput.setAttribute('match_ele', JSON.stringify(rects));
                        hiddenInput.setAttribute('iflyrpaKeys', 'match_ele');
                    }}

                    /**
                     * 查找并检查元素
                     */
                    function findAndCheckElementsForSelector(cssSelector, pathdirs, totalMatchedElements) {{
                        // 使用构建的选择器查找初始元素集
                        var initialElements = document.querySelectorAll(cssSelector);
                        var matchedElements = [];
                        //console.log(initialElements)
                        // 对每个初始元素进行深入检查
                        for (var i = 0; i < initialElements.length; i++) {{
                            var results = findMatchingElements(initialElements[i], pathdirs, 0);
                            for (var j = 0; j < results.length; j++) {{
                                matchedElements.push(results[j]);
                            }}
                        }}
                        //console.log(1111111)
                        //console.log(matchedElements)
                        // 合并结果
                        var updatedMatchedElements = totalMatchedElements.slice(); // 创建副本
                        for (var k = 0; k < matchedElements.length; k++) {{
                            updatedMatchedElements.push(matchedElements[k]);
                        }}

                        return updatedMatchedElements;
                    }}

                    /**
                     * 滚动查找元素
                     */
                    function scrollAndFindElements(cssSelector, pathdirs, totalMatchedElements, count, windowHeight) {{
                        window.scrollTo(window.scrollX, count * windowHeight);

                        setTimeout(function() {{
                            var updatedMatchedElements = findAndCheckElementsForSelector(
                                cssSelector, 
                                pathdirs, 
                                totalMatchedElements
                            );

                            if (updatedMatchedElements.length > 0) {{
                                handleMatchedElements(updatedMatchedElements);
                                return;
                            }}

                            if (count < SCROLL_TIMES) {{
                                scrollAndFindElements(
                                    cssSelector, 
                                    pathdirs, 
                                    updatedMatchedElements, 
                                    count + 1, 
                                    windowHeight
                                );
                            }} else {{
                                handleMatchedElements(updatedMatchedElements);
                            }}
                        }}, SCROLL_DELAY);
                    }}

                    /**
                     * 根据路径规则查找元素
                     */
                    function findElementBySelector(pathdirs) {{
                        var windowHeight = window.innerHeight || document.documentElement.clientHeight;
                        var windowScrollTop = document.documentElement.scrollTop || document.body.scrollTop;
                        var totalMatchedElements = [];

                        // 从pathdirs构建CSS选择器
                        var cssSelector = buildSelectorFromPathdir(pathdirs);

                        // 开始查找流程
                        totalMatchedElements = findAndCheckElementsForSelector(cssSelector, pathdirs, totalMatchedElements);

                        if (totalMatchedElements.length > 0) {{
                            handleMatchedElements(totalMatchedElements);
                            console.log(totalMatchedElements)
                            return;
                        }}else{{
                            console.log("没找到任何元素");
                        }}
                        if( {scroll_into_view_time}){{
                                return ;
                        }}

                        // 如果尚未滚动到底部且未找到匹配元素，则开始滚动查找
                        if (windowScrollTop < SCROLL_TIMES * windowHeight) {{
                            scrollAndFindElements(cssSelector, pathdirs, totalMatchedElements, 1, windowHeight);
                        }} else {{
                            handleMatchedElements(totalMatchedElements);
                        }}
                    }}
                      """.replace("{", "{{").replace("}", "}}")
            + """findElementBySelector("""
            + json.dumps(pathdirs, ensure_ascii=False).replace("{", "{{").replace("}", "}}")
            + ")"
        )
        res = IEAutomationClass().executeJsScroll(hwnd, script, int(iframeIndex), "wait use")["match_ele"]
        return res

    @classmethod
    def __check_xpath__(cls, xpath_str) -> bool:
        try:
            # 检查是否存在复杂语法（如//、@、*等）
            if "//" in xpath_str or "@" in xpath_str or "*" in xpath_str:
                return False
            # 分割路径步骤（例如：/div[1]/a[2] → ["div[1]", "a[2]"]）
            steps = xpath_str.strip("/").split("/")
            for step in steps:
                if not step:  # 空步骤跳过
                    continue
                # 分离标签名和谓词（如div[1] → tag=div, predicate=1）
                if "[" in step:
                    tag_part, predicate_part = step.split("[", 1)
                    predicate = predicate_part.split("]", 1)[0]
                    # 谓词必须是数字（如1或position()=1）
                    if not predicate.isdigit():
                        return False
                else:
                    tag_part = step
                # 标签名不能包含特殊字符（如函数调用或运算符）
                if not tag_part.isalnum():
                    return False
            return True
        except Exception as e:
            return False  # 表达式格式错误

    @classmethod
    def __modify_pathdir_attributes__(cls, pathDirs):
        # 遍历每个节点
        for node in pathDirs:
            # 遍历节点的所有属性
            for attr in node.get("attrs", []):
                # 仅处理非 @index 的属性
                if attr.get("name") != "@index":
                    attr["checked"] = False
                else:
                    attr["checked"] = True
        return pathDirs

    @classmethod
    def __get_web_top__(cls, ele: dict) -> tuple[int, int]:
        root_control = auto.GetRootControl()
        app_name = ele.get("app", "")

        ct = None
        for control, _ in auto.WalkControl(root_control, includeTop=True, maxDepth=1):
            if app_name == BrowserType.BTIE.value:
                if control.ClassName == "IEFrame":
                    ct = control
                    break
        if ct is None:
            return 0, 0

        # 置顶
        ct.SetActive()
        handle = ct.NativeWindowHandle
        top_window(handle, ct)
        if app_name == BrowserType.BTIE.value:
            notification_bar = ct.Control(searchDepth=1, ClassName="BrowserRootView")
            direct_ui = notification_bar.Control(searchDepth=1, ClassName="NonClientView")
            direct_ui = direct_ui.Control(searchDepth=1, ClassName="BrowserFrameViewWin")
            direct_ui = direct_ui.Control(searchDepth=1, ClassName="BrowserView")
            direct_ui = direct_ui.Control(searchDepth=1, ClassName="SidebarContentsSplitView")
            bounding_rect = direct_ui.BoundingRectangle
            top = bounding_rect.top
            left = bounding_rect.left
            return top, left
        return 0, 0


web_ie_factory = WebIEFactory()
