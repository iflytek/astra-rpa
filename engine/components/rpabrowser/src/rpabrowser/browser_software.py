import base64
import os
import platform
import shlex
import subprocess
import sys
import threading
import time
import webbrowser
from ast import literal_eval

import requests
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.types import PATH, URL, WebPick
from rpaframe.logger.logger import logger
from rpasoftware.software import Software

from rpabrowser import (
    BROWSER_PRIVATE_MAP,
    BROWSER_SOFTWARE_TAG,
    CHROME_LIKE_BROWSERS,
    ButtonForAssistiveKeyFlag,
    ButtonForClickTypeFlag,
    CommonForBrowserType,
    CommonForTimeoutHandleType,
    DownloadModeForFlag,
    ScreenShotForShotRangeFlag,
    WebSwitchType,
)
from rpabrowser.browser import Browser
from rpabrowser.browser_element import BrowserElement
from rpabrowser.core.core import IBrowserCore
from rpabrowser.error import (
    BROWSER_GET_TIMEOUT,
    BROWSER_NO_INSTALL,
    BROWSER_OPEN_TIMEOUT,
    BROWSER_PATH_EMPTY,
    PARAMETER_INVALID_FORMAT,
    SELECT_MATCHING_APP_PATH,
)

if sys.platform == "win32":
    from rpabrowser.core.core_win import BrowserCore
elif platform.system() == "Linux":
    from rpabrowser.core.core_unix import BrowserCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

BrowserCore: IBrowserCore = BrowserCore()


class BrowserSoftware:
    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        inputList=[
            atomicMg.param("wait_load_success", level=AtomicLevel.NORMAL, required=False),
            atomicMg.param(
                "browser_abs_path",
                level=AtomicLevel.NORMAL,
                required=False,
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
            atomicMg.param("open_args", level=AtomicLevel.ADVANCED, required=False),
            atomicMg.param(
                "open_with_incognito",
                formType=AtomicFormTypeMeta(type=AtomicFormType.CHECKBOX.value),
                level=AtomicLevel.ADVANCED,
                required=False,
            ),
            atomicMg.param(
                "timeout",
                level=AtomicLevel.NORMAL,
                dynamics=[
                    DynamicsItem(
                        key="$this.timeout.show",
                        expression="return $this.wait_load_success.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "timeout_handle_type",
                level=AtomicLevel.NORMAL,
                dynamics=[
                    DynamicsItem(
                        key="$this.timeout_handle_type.show",
                        expression="return $this.wait_load_success.value == true",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("web_open", types="Browser"),
        ],
    )
    def browser_open(
        url: URL,
        browser_type: CommonForBrowserType = CommonForBrowserType.BTChrome,
        browser_abs_path: PATH = "",
        open_args: str = "",
        open_with_incognito: bool = False,
        wait_load_success: bool = True,
        timeout: int = 20,
        timeout_handle_type: CommonForTimeoutHandleType = CommonForTimeoutHandleType.ExecError,
    ) -> Browser:
        """
        open 打开浏览器
        """
        open_args += " --remote-debugging-port=9555"

        if open_args and "--headless=old" in open_args:
            raise BaseException(BROWSER_OPEN_TIMEOUT, "浏览器不支持无头模式")

        if browser_type.value == "chromium":
            open_args += ' --load-extension="./Extensions/rpa-extension"'

        # 使用隐身模式时，需要添加 --incognito 参数
        if open_with_incognito:
            incognito_arg = BROWSER_PRIVATE_MAP.get(browser_type.value, "")
            if incognito_arg:
                open_args += f" --{incognito_arg}"

        if browser_abs_path and sys.platform == "win32":
            # 修改，获取浏览器执行文件后缀
            app_exe = os.path.basename(browser_abs_path)
            # 使用字典来简化条件判断
            software_tag_list = BROWSER_SOFTWARE_TAG.get(browser_type.value, None)
            if not (software_tag_list and (software_tag_list.lower() in app_exe.lower())):
                raise BaseException(
                    SELECT_MATCHING_APP_PATH.format(app_exe.lower()),
                    "请选择跟浏览器匹配的应用路径",
                )

        is_open = True
        # 获取地址
        res = Browser()
        res.browser_type = browser_type
        if not browser_abs_path:
            browser_abs_path = PATH(BrowserCore.get_browser_path(browser_type))
            logger.info(f"浏览器路径: {browser_abs_path}")
            if not browser_abs_path:
                raise BaseException(
                    BROWSER_PATH_EMPTY,
                    "注册表中未找到浏览器路径，请输入浏览器路径再运行 {}".format(browser_type),
                )
        res.browser_abs_path = browser_abs_path

        # 判断是否已经打开
        browser_file_name = browser_abs_path.file_name()
        browser_file_name = browser_file_name if browser_file_name != "IEXPLORE.EXE" else browser_file_name.lower()
        if not Software.exists(browser_file_name) or not BrowserCore.get_browser_handler(browser_type):
            # 判断是否已经打开，没有打开的话起新的
            is_open = False
            if browser_type in CHROME_LIKE_BROWSERS:
                webbrowser.BackgroundBrowser = GenericBrowser
                webbrowser.register(
                    browser_type.value,
                    None,
                    webbrowser.BackgroundBrowser(browser_abs_path),
                )
                webbrowser.get(browser_type.value).open(
                    str(url),
                    open_args=open_args,
                    open_with_incognito=open_with_incognito,
                )
            else:
                raise NotImplementedError()

        # 查询打开状态
        handler = None
        open_timeout = 10
        while open_timeout >= 0:
            handler = BrowserCore.get_browser_handler(browser_type)
            if handler:
                break
            time.sleep(1)
            open_timeout -= 1
        if not handler:
            raise BaseException(BROWSER_OPEN_TIMEOUT, "打开浏览器超时")
        time.sleep(1)

        # 置顶最大化
        if browser_type in CHROME_LIKE_BROWSERS:
            from rpawindow import WindowSizeType
            from rpawindow.window import WindowsCore

            WindowsCore.top(handler)
            WindowsCore.size(handler, WindowSizeType.MAX)
        else:
            raise NotImplementedError()

        if is_open:
            # 打开新标签页
            BrowserSoftware.web_open(browser_obj=res, new_tab_url=url)
        else:
            if browser_type in CHROME_LIKE_BROWSERS and not open_with_incognito:
                res.send_browser_extension(
                    browser_type=res.browser_type.value,  # '{{' + res.browser_type.value + '}}',
                    key="updateTab",
                    data={"url": str(url)},
                )

        BrowserSoftware.browser_max_window(browser_obj=res)

        # 等待网页加载完成
        if wait_load_success:
            result = BrowserSoftware.wait_web_load(browser_obj=res, timeout=timeout)
            if not result and timeout_handle_type == CommonForTimeoutHandleType.ExecError:
                BrowserSoftware.stop_web_load(browser_obj=res)
                # raise BaseException(WEB_LOAD_TIMEOUT, "打开网页超时，请重试 {}".format(result))
        return res

    @staticmethod
    @atomicMg.atomic("BrowserSoftware")
    def browser_close(browser_obj: Browser):
        """
        close 关闭浏览器
        """
        if not browser_obj.browser_abs_path:
            browser_obj.browser_abs_path = BrowserCore.get_browser_path(browser_obj.browser_type)
        Software.close(app_abs_path=browser_obj.browser_abs_path)

    @staticmethod
    def browser_max_window(browser_obj: Browser) -> bool:
        browser_type = browser_obj.browser_type
        if browser_type in CHROME_LIKE_BROWSERS:
            try:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="maxWindow",
                    data={"url": ""},
                )
                return True
            except Exception:
                return False
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        outputList=[
            atomicMg.param("cookie_input", types="Str"),
        ],
    )
    def set_cookies(
        browser_obj: Browser,
        url: URL,
        cookie_name: str,
        cookie_val: str,
        page_timeout: float = 10,
    ):
        """
        设置cookies
        """
        BrowserSoftware.wait_web_load(browser_obj, timeout=page_timeout)
        browser_type = browser_obj.browser_type
        if browser_type in CHROME_LIKE_BROWSERS:
            browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="setCookies",
                data={"url": str(url), "name": cookie_name, "value": cookie_val},
            )
        else:
            raise NotImplementedError()
        return cookie_val

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        outputList=[
            atomicMg.param("get_cookie", types="Str"),
        ],
    )
    def get_cookies(browser_obj: Browser, url: URL, cookie_name: str, page_timeout: float = 10) -> str:
        """
        获取cookies
        """
        browser_type = browser_obj.browser_type
        BrowserSoftware.wait_web_load(browser_obj, timeout=page_timeout)
        if browser_type in CHROME_LIKE_BROWSERS:
            data = browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="getCookie",
                data={"url": str(url), "name": cookie_name},
            )

            data = data["value"]
        else:
            raise NotImplementedError()
        return str(data)

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        outputList=[
            atomicMg.param("web_new_page", types="Browser"),
        ],
    )
    def web_open(browser_obj: Browser, new_tab_url: URL = "", wait_page: bool = True) -> "Browser":
        """打开新网页"""
        browser_type = browser_obj.browser_type
        new_tab_url = URL.__validate__("", str(new_tab_url))
        if browser_type in CHROME_LIKE_BROWSERS:
            browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="openNewTab",
                data={"url": str(new_tab_url)},
            )
        else:
            raise NotImplementedError()
        if wait_page:
            BrowserSoftware.wait_web_load(browser_obj, timeout=20)
        return browser_obj

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        inputList=[
            atomicMg.param(
                "tab_url",
                dynamics=[
                    DynamicsItem(
                        key="$this.tab_url.show",
                        expression=f"return $this.switch_type.value == '{WebSwitchType.URL.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "tab_title",
                dynamics=[
                    DynamicsItem(
                        key="$this.tab_title.show",
                        expression=f"return $this.switch_type.value == '{WebSwitchType.TITLE.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "tab_id",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.tab_id.show",
                        expression=f"return $this.switch_type.value == '{WebSwitchType.TabId.value}'",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("toggle_tab", types="Str"),
        ],
    )
    def web_switch(
        browser_obj: Browser,
        switch_type: WebSwitchType = WebSwitchType.URL,
        tab_url: str = "",
        tab_title: str = "",
        tab_id: int = 0,
    ) -> str:
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            if switch_type == WebSwitchType.URL:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="switchTab",
                    data={"url": tab_url},
                )
            elif switch_type == WebSwitchType.TabId:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="switchTab",
                    data={"id": tab_id},
                )
            else:
                browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="switchTab",
                    data={"title": tab_title},
                )
        else:
            raise NotImplementedError()
        return tab_url if switch_type == WebSwitchType.URL else tab_title

    @staticmethod
    @atomicMg.atomic("BrowserSoftware")
    def wait_web_load(browser_obj: Browser, timeout: int = 20) -> bool:
        """
        等待页面加载完成，直到超时或页面加载完成。
        """
        timeout = float(timeout)
        if timeout < 0:
            raise BaseException(
                PARAMETER_INVALID_FORMAT.format(timeout),
                f"等待时间不能小于0！{timeout}",
            )

        end = time.time() + timeout
        while time.time() < end:
            time.sleep(0.3)
            try:
                if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
                    data = browser_obj.send_browser_extension(
                        browser_type=browser_obj.browser_type.value,
                        key="loadComplete",
                        data={"": ""},
                    )
                else:
                    raise NotImplementedError()
                if data:
                    return True
            except Exception:
                pass
        return False

    @staticmethod
    @atomicMg.atomic("BrowserSoftware")
    def stop_web_load(browser_obj: Browser):
        """
        停止加载网页
        """
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="stopLoad",
                data={"": ""},
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic("BrowserSoftware")
    def web_refresh(browser_obj: Browser):
        """
        刷新网页
        """
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="reloadTab",
                data={"": ""},
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic("BrowserSoftware", inputList=[atomicMg.param("url", required=False)])
    def web_close(browser_obj: Browser, url: str = ""):
        """
        关闭网页
        """
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="closeTab",
                data={"url": url},
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        inputList=[
            atomicMg.param(
                "image_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("web_screen", types="Str"),
        ],
    )
    def screenshot(
        browser_obj: Browser,
        shot_range: ScreenShotForShotRangeFlag = ScreenShotForShotRangeFlag.Visual,
        image_path: str = "",
        image_name: str = "",
        page_timeout: float = 10,
    ) -> str:
        if not image_name.endswith((".png", ".jpg", ".jpeg")):
            image_name += ".jpg"
        BrowserSoftware.wait_web_load(browser_obj, timeout=page_timeout)
        dest_path = os.path.join(image_path, image_name)
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            if shot_range == ScreenShotForShotRangeFlag.Visual:
                data = browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="captureScreen",
                    data={"": ""},
                    timeout=30,
                )
            elif shot_range == ScreenShotForShotRangeFlag.All:
                data = browser_obj.send_browser_extension(
                    browser_type=browser_obj.browser_type.value,
                    key="capturePage",
                    data={"": ""},
                    timeout=30,
                )
            else:
                raise NotImplementedError()
            if data:
                data = data.replace("data:image/jpeg;base64,", "")
            else:
                raise Exception("插件返回数据为空")
            with open(dest_path, "wb") as f:
                f.write(base64.b64decode(data))
        return dest_path

    @staticmethod
    @atomicMg.atomic("BrowserSoftware")
    def browser_forward(
        browser_obj: Browser,
    ):
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="forward",
                data={"": ""},
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic("BrowserSoftware")
    def browser_back(
        browser_obj: Browser,
    ):
        if browser_obj.browser_type in CHROME_LIKE_BROWSERS:
            browser_obj.send_browser_extension(
                browser_type=browser_obj.browser_type.value,
                key="backward",
                data={"": ""},
            )
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        outputList=[
            atomicMg.param("browser_obj", types="Browser"),
        ],
    )
    def get_current_obj(
        browser_type: CommonForBrowserType = CommonForBrowserType.BTChrome,
    ) -> Browser:
        br = Browser()
        br.browser_type = browser_type
        # 查询打开状态
        handler = None
        open_timeout = 10
        while open_timeout >= 0:
            handler = BrowserCore.get_browser_handler(browser_type)
            if handler:
                break
            time.sleep(1)
            open_timeout -= 1
        if not handler:
            raise BaseException(BROWSER_GET_TIMEOUT, "")
        # 置顶最大化
        if browser_type in CHROME_LIKE_BROWSERS:
            from rpawindow import WindowSizeType
            from rpawindow.window import WindowsCore

            WindowsCore.top(handler)
            WindowsCore.size(handler, WindowSizeType.MAX)
        else:
            raise NotImplementedError()
        return br

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        outputList=[
            atomicMg.param("get_url", types="Str"),
        ],
    )
    def get_current_url(browser_obj: Browser) -> str:
        return browser_obj.get_url()

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        outputList=[
            atomicMg.param("get_page_title", types="Str"),
        ],
    )
    def get_current_title(browser_obj: Browser) -> str:
        return browser_obj.get_title()

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        outputList=[
            atomicMg.param("get_tab_id", types="Int"),
        ],
    )
    def get_current_tab_id(browser_obj: Browser) -> int:
        return browser_obj.get_tabid()

    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        inputList=[
            atomicMg.param("custom_flag", required=False),
            atomicMg.param(
                "save_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "simulate_flag",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.simulate_flag.show",
                        expression=f"return $this.download_mode.value == '{DownloadModeForFlag.Click.value}'",
                    )
                ],
            ),
            atomicMg.param("is_wait", required=False),
            atomicMg.param(
                "time_out",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.time_out.show",
                        expression="return $this.is_wait.value == true",
                    )
                ],
            ),
            atomicMg.param(
                "element_data",
                dynamics=[
                    DynamicsItem(
                        key="$this.element_data.show",
                        expression=f"return $this.download_mode.value == '{DownloadModeForFlag.Click.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "link_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.link_str.show",
                        expression=f"return $this.download_mode.value == '{DownloadModeForFlag.Link.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.custom_flag.value == true",
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("load_file", types="Str"),
        ],
    )
    def download_web_file(
        browser_obj: Browser,
        element_data: WebPick,
        download_mode: DownloadModeForFlag = DownloadModeForFlag.Click,
        link_str: str = "",
        save_path: str = "",
        custom_flag: bool = False,
        file_name: str = "",
        simulate_flag: bool = True,
        is_wait: bool = True,
        time_out: int = 60,
    ):
        if download_mode == DownloadModeForFlag.Click:
            default_save_path = os.path.join(os.path.expanduser("~"), "Downloads")
            origin_files = os.listdir(default_save_path)
            BrowserElement.click(
                browser_obj=browser_obj,
                element_data=element_data,
                simulate_flag=simulate_flag,
                assistive_key=ButtonForAssistiveKeyFlag.Nothing,
                button_type=ButtonForClickTypeFlag.Left,
                element_timeout=10,
            )
            dest_path = BrowserCore.download_window_operate(
                browser_type=browser_obj.browser_type,
                is_wait=is_wait,
                time_out=time_out,
                file_name=file_name,
                custom_flag=custom_flag,
                save_path=save_path,
            )
            return dest_path
        elif download_mode == DownloadModeForFlag.Link:
            """通过网页链接下载"""
            file_path_arr = []
            if not (link_str and save_path):
                raise ValueError("请提供正确的url链接和文件存储路径")
            try:
                link_strs = literal_eval(link_str)
            except Exception:
                link_strs = [link_str]
            down_tag = []

            def download_from_req(file_name_out):
                for link_item in link_strs:
                    url_file = link_item.split("?")[0]
                    res = requests.get(link_item, timeout=300, allow_redirects=True, stream=True)
                    if res.status_code != 200:
                        raise requests.RequestException("请求的地址异常")
                    if not custom_flag:
                        file_name_out = url_file.split("/")[-1]
                    else:
                        file_name_out = file_name_out + "." + url_file.split("/")[-1].rsplit(".", 1)[-1]
                    file_path = os.path.join(save_path, file_name_out)
                    file_path_arr.append(file_path)
                    with open(file_path, "wb") as f:
                        for chunk in res.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                down_tag.append(1)

            if is_wait:
                if time_out == 0 or time_out == "":
                    download_from_req(file_name)
                else:
                    threading.Thread(target=download_from_req, args=(file_name,)).start()
                    try:
                        wait_time_download = int(time_out)
                    except Exception:
                        wait_time_download = 60
                    while wait_time_download > 0:
                        wait_time_download = wait_time_download - 3
                        if len(down_tag) > 0:
                            break
                        time.sleep(3)
                    # 需要确定好链接下载是多个还是单个
                    # if wait_time_download<=0 and not os.path.exists(file_name):
                    #     raise Exception("等待下载完成超时")
                return file_path_arr
            else:
                threading.Thread(target=download_from_req, args=(file_name,)).start()
                return save_path

    # 上传文件逻辑
    @staticmethod
    @atomicMg.atomic(
        "BrowserSoftware",
        inputList=[
            atomicMg.param("simulate_flag", required=False),
            atomicMg.param(
                "upload_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("download_file", types="Str"),
        ],
    )
    def upload_web_file(
        browser_obj: Browser,
        element_data: WebPick = None,
        upload_path: str = "",
        simulate_flag: bool = True,
    ):
        BrowserElement.click(
            browser_obj=browser_obj,
            element_data=element_data,
            simulate_flag=simulate_flag,
            assistive_key=ButtonForAssistiveKeyFlag.Nothing,
            button_type=ButtonForClickTypeFlag.Left,
            element_timeout=10,
        )
        BrowserCore.upload_window_operate(browser_type=browser_obj.browser_type, upload_path=upload_path)


class GenericBrowser(webbrowser.GenericBrowser):
    def open(self, url, new=0, autoraise=True, open_args=None, open_with_incognito=None):
        logger.info(f"打开浏览器的输入参数{open_args}")
        url_showed = [url]
        if open_args is None:
            open_args = ""
            # 添加必要的参数，例如 --new-window 或 --app
        if "--new-window" not in open_args:
            open_args += " --new-window"
        if open_with_incognito:
            url_showed = [arg.replace("%s", url) for arg in self.args]
        cmdline = [self.name] + shlex.split(open_args) + url_showed
        logger.info(f"测试命令行{cmdline}")
        try:
            if sys.platform[:3] == "win":
                p = subprocess.Popen(cmdline)
            else:
                p = subprocess.Popen(cmdline, close_fds=True, start_new_session=True)
            while not p.pid:
                time.sleep(0.3)
            time.sleep(1)
            return p.poll() is None
        except FileNotFoundError as e:
            raise BaseException(BROWSER_NO_INSTALL, f"该浏览器暂未安装！{e}")
        except OSError:
            return False
