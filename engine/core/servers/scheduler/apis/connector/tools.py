import asyncio
import datetime
import json
import mimetypes
import os
import sys
from dataclasses import field
from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator

from ...apis.response import ResCode, res_msg
from ...core.environment.venv import create_project_venv
from ...core.svc import Svc, get_svc
from ...logger import logger
from ...utils.ai import InputType, get_factors
from ...utils.clipboard import Clipboard
from ...utils.pip import PipManager
from ...utils.platform_utils import platform_python_venv_path
from ...utils.subprocess import SubPopen
from ...utils.utils import EmitType, emit_to_front

router = APIRouter()


class FilePath(BaseModel):
    path: str


class WriteFile(BaseModel):
    path: str
    mode: str = "w"  # w 覆盖写 a 追加写
    content: str


class VideoPaths(BaseModel):
    videoPaths: list


class BrowserPlugin(BaseModel):
    """
    定义安装插件参数
    """

    browser: str = "chrome"
    op: str = "install"


class BrowserType(Enum):
    CHROME = "CHROME"


class ContractFactors(Enum):
    contract_type: InputType = InputType.TEXT
    contract_path: str = ""
    contract_content: str = ""
    custom_factors: str = ""
    contract_validate: str = ""


class CheckBrowserPlugin(BaseModel):
    """
    定义检测安装插件参数
    """

    browsers: List[str] = field(default_factory=list)

    @classmethod
    @field_validator("browsers", mode="before")
    def set_default_browsers(cls, v):
        default_browser_list = [browser.value.lower() for browser in BrowserType]
        if not v:
            return default_browser_list
        assert all(item in default_browser_list for item in v), "Invalid browser type in plugins"
        return v


class PipPackages(BaseModel):
    """
    定义安装python包信息
    """

    project_id: str
    package: str = ""
    version: str = ""
    mirror: str = ""


class NotifyText(BaseModel):
    alert_type: str


class ClipboardParams(BaseModel):
    is_html: bool = False


@router.on_event("startup")
async def startup_event():
    async def startup():
        emit_to_front(
            EmitType.SYNC_CANCEL,
            msg={"route_port": get_svc().route_port, "step": 100},
        )

    task = asyncio.create_task(startup())


@router.post("/file/read")
def read_file(file_path: FilePath):
    """
    前端通用的读取文件的方法，包括日志文件
    """
    # 检查文件是否存在
    if not os.path.isfile(file_path.path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        mime_type, _ = mimetypes.guess_type(file_path.path)
        if mime_type is None:
            mime_type = "application/octet-stream"  # 默认 MIME 类型

        def file_iterator():
            with open(file_path.path, "rb") as file:
                while True:
                    chunk = file.read(1024)  # 每次读取 1024 字节
                    if not chunk:
                        break
                    yield chunk

        return StreamingResponse(file_iterator(), media_type=mime_type)
    except Exception as e:
        logger.exception("read_file error: {}".format(e))
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/file/write")
def read_write(write_file: WriteFile):
    """
    前端通用的覆盖写文件的方法
    """
    # 检查文件夹是否存在
    if not os.path.exists(os.path.dirname(write_file.path)):
        os.mkdir(os.path.dirname(write_file.path))

    # 写入文件
    try:
        with open(write_file.path, "w") as f:
            f.write(write_file.content)
        return res_msg(code=ResCode.SUCCESS, msg="", data=None)
    except Exception as e:
        logger.exception("read_write error: {}".format(e))
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/video/play")
def video_play(video_paths: VideoPaths):
    try:
        video_paths = video_paths.videoPaths
        if not video_paths:
            return res_msg(code=ResCode.ERR, msg="videoPaths is empty", data={"exist": []})
        existing_files = [path for path in video_paths if os.path.exists(path)]
        return res_msg(code=ResCode.SUCCESS, msg="", data={"exist": existing_files})
    except Exception as e:
        logger.exception("An error occurred while checking video paths.")
        return res_msg(code=ResCode.ERR, msg=str(e), data=None)


@router.post("/window/auto_start/check")
def auto_start_check():
    """
    自启动探测
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"autostart": False})

    from ...utils.window import AutoStart

    return res_msg(msg="", data={"autostart": AutoStart.check()})


@router.post("/window/auto_start/enable")
def auto_start_enable(svc: Svc = Depends(get_svc)):
    """
    自动开启
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"tips": "操作异常，linux暂不支持自启动"})

    from ...utils.window import AutoStart

    exe_path = os.path.join(os.path.dirname(os.path.dirname(svc.config.app_server.conf_file)), "iflyrpa.exe").lower()
    AutoStart.enable(exe_path)
    return res_msg(msg="", data={"tips": "操作成功"})


@router.post("/window/auto_start/disable")
def auto_start_disable():
    """
    自启动关闭
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"tips": "操作异常，linux暂不支持自启动"})

    from ...utils.window import AutoStart

    AutoStart.disable()
    return res_msg(msg="", data={"tips": "操作成功"})


@router.get("/browser/plugins/get_support")
def browser_get_support():
    """
    获取插件支持的浏览器列表
    """
    try:
        from .....extensions.browser_plugin.browser import ExtensionManager
        from .....extensions.browser_plugin.constants import BrowserType

        browsers = [browser.value.lower() for browser in ExtensionManager.get_support()]
        return res_msg(msg="获取成功", data={"browsers": browsers})
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="获取失败", data=None)


@router.post("/browser/plugins/install")
def browser_install(plugin_op: BrowserPlugin):
    """
    安装插件
    """
    try:
        from .....extensions.browser_plugin.browser import ExtensionManager
        from .....extensions.browser_plugin.constants import BrowserType

        browser = BrowserType.init(plugin_op.browser)
        ex_manager = ExtensionManager(browser_type=browser)
        ex_manager.install()
        return res_msg(msg="安装成功", data=None)
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="安装失败", data=None)


@router.post("/browser/plugins/check_status")
def browser_check(options: CheckBrowserPlugin):
    """
    检测插件状态
    """
    try:
        from .....extensions.browser_plugin.browser import ExtensionManager
        from .....extensions.browser_plugin.constants import BrowserType

        check_result = dict()
        for browser in options.browsers:
            ex_manager = ExtensionManager(browser_type=BrowserType.init(browser))
            check_result[browser.lower()] = ex_manager.check_status()
        return res_msg(msg="", data=check_result)
    except Exception as e:
        logger.exception(e)
    return res_msg(code=ResCode.ERR, msg="检测失败", data=None)


@router.post("/clipboard/get")
def clipboard_get(is_html: bool):
    """
    获取剪贴板内容
    """
    from ...utils.clipboard import Clipboard

    if is_html:
        content = Clipboard.paste_html_clip()
    else:
        content = Clipboard.paste_str_clip()
    return res_msg(code=ResCode.SUCCESS, msg="", data={"content": content})


@router.post("/pip/install")
def stream_sse(pck: PipPackages, svc: Svc = Depends(get_svc)):
    def sse_async_generator(pck: PipPackages):
        """
        实现前端包安装交互
        """
        sub_processes = list()
        try:
            project_id = pck.project_id
            package = pck.package
            version = pck.version
            mirror = pck.mirror
            create_project_venv(svc, project_id)
            pck_v = package
            if version:
                pck_v += "=={}".format(version)
            v_path = os.path.join(svc.config.app_server.venv_base_dir, project_id)
            exec_python = platform_python_venv_path(v_path)

            def log(sub_proc):
                while True:
                    output = sub_proc.proc.stdout.readline()
                    if output == "" and not sub_proc.is_alive():
                        break
                    if not output.strip():
                        continue
                    yield "data: {}\n\n".format(json.dumps({"stdout": output}))
                    if "Successfully installed {}".format(package) in output:
                        return
                err_info = sub_proc.proc.stderr.read().strip()
                if err_info:
                    raise Exception(err_info)

            # 下载并缓存
            download_proc = SubPopen(cmd=PipManager.download_pip_cmd(package, version, mirror)).run(log=True)
            sub_processes.append(download_proc)
            for log_data in log(download_proc):
                yield log_data

            # 执行安装
            install_proc = SubPopen(cmd=PipManager.install_pip_cmd(package, version, exec_python=exec_python)).run(
                log=True
            )
            sub_processes.append(download_proc)
            for log_data in log(install_proc):
                yield log_data
        except Exception as e:
            logger.exception(e)
            err = str(e)
            data = json.dumps({"stderr": err})
            yield f"data: {data}\n\n"
        finally:
            for sub_pro in sub_processes:
                sub_pro.kill()
            yield f"event: done\ndata: [DONE]\n\n"

    return StreamingResponse(sse_async_generator(pck), media_type="text/event-stream")


@router.post("/package/version")
def package_version(pck: PipPackages, svc: Svc = Depends(get_svc)):
    package = pck.package
    project_id = pck.project_id
    v_path = os.path.join(svc.config.app_server.venv_base_dir, project_id)
    exec_python = platform_python_venv_path(v_path)
    if os.path.exists(exec_python):
        version = PipManager.package_version(package, exec_python=exec_python)
    else:
        version = None
    return res_msg(msg="", data={"package": package, "version": version})


@router.post("/alert/test")
def notify_text(param: NotifyText, svc: Svc = Depends(get_svc)):
    from ...utils.notify_utils import NotifyUtils

    notifier = NotifyUtils(svc)
    if param.alert_type == "mail":
        if not notifier.email_setting["receiver"]:
            return res_msg(code=ResCode.ERR, msg="邮件必填", data=None)

        notifier.login_send()
        notifier.send_email("测试邮件")
    else:
        if not notifier.text_setting["receiver"]:
            return res_msg(code=ResCode.ERR, msg="手机号必填", data=None)

        notifier.send_text("test", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/send/tip")
def send_tip(tip_data: dict, svc: Svc = Depends(get_svc)):
    emit_to_front(EmitType.TIP, msg=tip_data)
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/send/alert")
def send_tip(tip_data: dict, svc: Svc = Depends(get_svc)):
    emit_to_front(EmitType.ALERT, msg=tip_data)
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/validate/contract")
def validate_contract(params: ContractFactors, svc: Svc = Depends(get_svc)):
    logger.info(f"params: {params}")
    get_factors(
        params.contract_type,
        params.contract_path,
        params.contract_content,
        params.custom_factors,
        params.contract_validate,
        svc.route_port,
    )
    return res_msg(code=ResCode.SUCCESS, msg="", data=None)


@router.post("/clipboard")
def get_clipboard_html(params: ClipboardParams, svc: Svc = Depends(get_svc)):
    content = ""
    if params.is_html:
        content = Clipboard.paste_html_clip()
    else:
        content = Clipboard.paste_str_clip()
    return res_msg(code=ResCode.SUCCESS, msg="", data={"content": content})
