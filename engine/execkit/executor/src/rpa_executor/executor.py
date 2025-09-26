import copy
import time
import traceback
from typing import Any, Optional

from rpaatomic import (
    ReportCode,
    ReportCodeStatus,
    ReportFlow,
    ReportFlowStatus,
    ReportType,
)

from rpa_executor import ExecuteStatus, ProcessInfo, ProjectInfo
from rpa_executor.error import *
from rpa_executor.flow.svc import Svc
from rpa_executor.flow.syntax import Token
from rpa_executor.flow.syntax.environment import EnvBizTypes, EnvItem
from rpa_executor.flow.syntax.event import CloseError, EventKey, event
from rpa_executor.flow.syntax.lexer import Lexer
from rpa_executor.flow.syntax.parser import Parser
from rpa_executor.flow.syntax.token import TokenType


def flow_to_token(flow_json: dict) -> Optional[Token]:
    """将flow转换成token"""

    token_type = flow_json.get("key")
    if not token_type:
        raise Exception("Lexer error: missing key {}".format(flow_json))
    if token_type in [TokenType.Group.value, TokenType.GroupEnd.value]:
        return
    disabled = flow_json.get("disabled")
    if disabled:
        return
    return Token(token_type, flow_json)


class Executor:
    def __init__(self, svc: Svc, max_append_child_size: int = 100):
        self.svc = svc

        # 使用环检测也是可以的，这种相对简单
        self.append_child_size = 0
        self.max_append_child_size = max_append_child_size

    def error_logger_handler(self, svc, env, token: Token, func, *args, **war_kwargs):
        """普通eval的错误日志handler"""

        try:
            return python_base_error(func)(*args, **war_kwargs)
        except IgnoreException as e:
            raise e
        except Exception as e:
            # 需要捕获用户错误
            if isinstance(e, BaseException):
                error_str = e.code.message
            else:
                error_str = str(e)

            input_list = token.value.get("inputList", [])
            error_type = None
            for i in input_list:
                if i.get("key") == "__skip_err__":
                    error_type = i.get("value")
                    break
            if error_type == "skip":
                self.svc.report.warning(
                    ReportCode(
                        log_type=ReportType.Code,
                        process=token.value.get("__process_name__", ""),
                        process_id=token.value.get("__process_id__", ""),
                        atomic=token.value.get("anotherName", token.value.get("title", "")),
                        line=token.value.get("__line__", 0),
                        line_id=token.value.get("id", ""),
                        status=ReportCodeStatus.SKIP,
                        msg_str="{} {}".format(ReportCodeSkip, error_str),
                        error_traceback=traceback.format_exc(),
                    )
                )
            else:
                self.svc.report.error(
                    ReportCode(
                        log_type=ReportType.Code,
                        process=token.value.get("__process_name__", ""),
                        process_id=token.value.get("__process_id__", ""),
                        atomic=token.value.get("anotherName", token.value.get("title", "")),
                        line=token.value.get("__line__", 0),
                        line_id=token.value.get("id", ""),
                        status=ReportCodeStatus.ERROR,
                        msg_str="{} {}".format(ReportCodeError, error_str),
                        error_traceback=traceback.format_exc(),
                    )
                )
                raise IgnoreException() from e

    def debug_handler(self, svc, env, token):
        """调试模式处理类"""

        if not svc.debug:
            return

        line = int(token.value.get("__line__", 0))
        process_id = token.value.get("__process_id__", "")
        project_id = token.value.get("__project_id__", "")

        if EventKey.STACK.value not in svc.events:
            svc.events[EventKey.STACK.value] = [process_id]
        elif len(svc.events[EventKey.STACK.value]) >= 2 and svc.events[EventKey.STACK.value][-2] == process_id:
            svc.events[EventKey.STACK.value].pop()
        elif len(svc.events[EventKey.STACK.value]) >= 1 and svc.events[EventKey.STACK.value][-1] != process_id:
            svc.events[EventKey.STACK.value].append(process_id)

        def wait():
            while True:
                if svc.events.get(EventKey.Next.value):
                    svc.events[EventKey.ResNext.value] = True
                    svc.events[EventKey.Next.value] = False

                    svc.events[EventKey.PreNext.value] = dict.fromkeys(svc.events[EventKey.STACK.value], True)
                    break
                if svc.events.get(EventKey.Continue.value):
                    svc.events[EventKey.ResContinue.value] = True
                    svc.events[EventKey.Continue.value] = False
                    break
                time.sleep(0.3)
                event.raw_event_handler(svc)

        is_break = False
        if EventKey.PreNext.value in svc.events and process_id in svc.events[EventKey.PreNext.value]:
            del svc.events[EventKey.PreNext.value]
            is_break = True
        elif EventKey.LINE.value not in svc.events or (
            EventKey.Break.value in svc.events and "{}-{}".format(process_id, line) in svc.events[EventKey.Break.value]
        ):
            is_break = True

        self.svc.report.info(
            ReportCode(
                log_type=ReportType.Code,
                process=token.value.get("__process_name__", ""),
                process_id=process_id,
                atomic=token.value.get("anotherName", token.value.get("title", "")),
                line=line,
                line_id=token.value.get("id", ""),
                status=ReportCodeStatus.DEBUG_START,
                msg_str=ReportDebugStartMsgFormat.format(
                    token.value.get("__process_name__", ""),
                    line,
                    token.value.get("anotherName", token.value.get("title", "")),
                ),
                debug_data={
                    "is_break": is_break,
                    "data": env.to_json_dict(project_id) if is_break else None,
                },
            )
        )

        if is_break:
            wait()
        svc.events[EventKey.LINE.value] = line

    def get_flow_list(self, project_id, process_id, mode, version) -> list:
        """通过远端获取flow_list"""
        line = 0
        if self.svc.process_dict[process_id].flow is None:
            flow_list = self.svc.storage.process_json(project_id, process_id, mode, version)
            for k, v in enumerate(flow_list):
                line = line + 1
                v.update(
                    {
                        "__line__": line,
                        "__project_id__": project_id,
                        "__process_id__": process_id,
                        "__process_name__": self.svc.process_dict[process_id].name,
                    }
                )
                if project_id == self.svc.start_project_id:
                    # 只有启动工程才有断点的能力
                    if v.get("breakpoint"):
                        self.svc.event_break()["{}-{}".format(process_id, v.get("__line__"))] = True

            # 更新参数信息和flow信息
            flow_param = self.svc.storage.param_list(project_id, process_id, mode, version)
            self.svc.process_dict[process_id].param = flow_param
            self.svc.process_dict[process_id].flow = flow_list
        return copy.deepcopy(self.svc.process_dict[process_id].flow)

    def append_child_flow_list(self, flow, flow_list, read_position):
        """添加子流程flow_list"""
        disabled = flow.get("disabled", None)
        if disabled:
            return

        self.append_child_size += 1
        if self.append_child_size > self.max_append_child_size:
            raise BaseException(
                RECURSIVE_CALL_MAX_FORMAT.format(self.max_append_child_size),
                "加载子流程超过{}上限，可能是循环引用".format(self.max_append_child_size),
            )

        if flow.get("key") == TokenType.Process.value and "__temp_process_end__" not in flow:
            project_id = flow.get("__project_id__")
            process_id = flow.get("__process_id__")
            project_info = self.svc.project_dict[project_id]

            new_process_id = flow.get("inputList")[0].get("value")
            if not new_process_id:
                raise BaseException(CHILD_PROCESS_PARAM_NOT_VALID, "子流程参数不合法")
            if new_process_id == process_id:
                raise BaseException(RECURSIVE_CALL, "循环引用")

            # 打上标志，表示已经处理过了
            flow["__temp_process_end__"] = True

            # 1. 获取子流程flow_list，并添加到flow_list中
            pre = flow_list[: read_position + 1]
            child_flow_list = self.get_flow_list(
                project_id,
                new_process_id,
                project_info.project_mode,
                project_info.project_version,
            )
            pre.extend(child_flow_list)

            # 2. flow_list最后再添加一个结束标志位主要是为了解析
            end = copy.deepcopy(flow)
            end["id"] = flow["id"] + "1"
            end["key"] = TokenType.ProcessEnd.value
            end["relationStartId"] = flow["id"]
            end["__temp_process_end__"] = True
            pre.append(end)

            # 3. 把剩余的再回去
            aft = flow_list[read_position + 1 :]
            if len(aft) > 0:
                pre.extend(aft)
            return pre
        elif flow.get("key").startswith(TokenType.Component.value) and "__temp_process_end__" not in flow:
            project_id = flow.get("__project_id__")
            new_project_id = flow.get("key").split(".")[-1]

            if not new_project_id:
                raise BaseException(CHILD_PROCESS_PARAM_NOT_VALID, "子流程参数不合法")
            if new_project_id == project_id:
                raise BaseException(RECURSIVE_CALL, "循环引用")
            new_project_info = self.svc.project_dict[new_project_id]

            new_process_id = 0
            for i in self.svc.process_dict.values():
                if new_project_id == i.project_id and i.is_default_main:
                    new_process_id = i.process_id

            # 打上标志，表示已经处理过了
            flow["key"] = TokenType.Component.value
            flow["__line__"] = 0
            flow["__project_id__"] = new_project_id
            flow["__process_id__"] = new_process_id
            flow["__temp_process_end__"] = True

            # 1. 获取子流程flow_list，并添加到flow_list中
            pre = flow_list[: read_position + 1]
            child_flow_list = self.get_flow_list(
                new_project_id,
                new_process_id,
                new_project_info.project_mode,
                new_project_info.project_version,
            )
            pre.extend(child_flow_list)

            # 2. flow_list最后再添加一个结束标志位主要是为了解析
            end = copy.deepcopy(flow)
            end["id"] = flow["id"] + "1"
            end["key"] = TokenType.ComponentEnd.value
            end["relationStartId"] = flow["id"]
            end["__temp_process_end__"] = True
            pre.append(end)

            # 3. 把剩余的再回去
            aft = flow_list[read_position + 1 :]
            if len(aft) > 0:
                pre.extend(aft)
            return pre

    def project_init(
        self,
        project_id: str,
        process_id: str = "",
        mode: str = "",
        version: str = "",
        line: int = 0,
        end_line: int = 0,
        env=None,
    ) -> Any:
        """初始化工程"""

        def raw_project_init():
            nonlocal process_id
            self.svc.storage.report_status_upload("execute", "")

            # 日志1
            self.svc.report.info(
                ReportFlow(
                    log_type=ReportType.Flow,
                    status=ReportFlowStatus.INIT,
                    msg_str=ReportFlowInit,
                )
            )

            # 获取需要加载的project, 包含组件
            self.svc.project_dict[project_id] = ProjectInfo(
                project_id=project_id,
                project_mode=mode,
                project_version=version,
            )
            component_list = self.svc.storage.component_list(project_id, mode, version)
            if component_list:
                for c in component_list:
                    self.svc.project_dict[c.get("componentId")] = ProjectInfo(
                        project_id=c.get("componentId"),
                        project_mode="",
                        project_version=c.get("version"),
                    )

            # 获取配置-流程获取
            process_dict = {}
            for p in self.svc.project_dict.values():
                process_list = self.svc.storage.process_list(p.project_id, p.project_mode, p.project_version)
                if len(process_list) == 0:
                    raise BaseException(ENGINEERING_DATA_ERROR, "工程数据异常 {}".format(project_id))
                for i, v in enumerate(process_list):
                    process_dict[v.get("processId")] = ProcessInfo(
                        name=v.get("processName"),
                        project_id=p.project_id,
                        process_id=v.get("processId"),
                    )
                    if i == 0:
                        process_dict[v.get("processId")].is_default_main = True

                # 如果是传入的project_id，需要进一步判断一下传入project_id是否合法
                if p.project_id == project_id:
                    if process_id:
                        if process_id not in process_dict:
                            raise BaseException(
                                ENGINEERING_DATA_ERROR,
                                "工程数据异常 {}".format(process_id),
                            )
                    else:
                        process_id = process_list[0].get("processId")
            self.svc.start_process_id = process_id
            self.svc.process_dict = process_dict

            # 词法解析
            flow_list = self.get_flow_list(project_id, process_id, mode, version)
            if line > 0 and end_line == 0:
                # 从此处执行逻辑
                for flow in flow_list:
                    if flow.get("__line__") == line:
                        break
                    else:
                        flow["disabled"] = True
            elif line > 0 and end_line > 0:
                # 选择逻辑
                if line == end_line:
                    self.svc.line_debug = "{}-{}".format(process_id, line)
                for flow in flow_list:
                    if line <= flow.get("__line__") <= end_line:
                        continue
                    else:
                        flow["disabled"] = True
            else:
                # 正常逻辑
                pass
            lexer = Lexer(flow_list, flow_to_token, self.append_child_flow_list)

            # 语法解析
            parser = Parser(lexer=lexer)
            program = parser.parse_program()
            if len(parser.errors) > 0:
                raise BaseException(
                    SYNTAX_ERROR_FORMAT.format(" ".join(parser.errors)),
                    "语法错误: {}".format(parser.errors),
                )

            # 全局环境变量
            import os

            os.environ["GATEWAY_PORT"] = self.svc.gateway_port
            os.environ["PROJECT_ID"] = project_id

            import importlib

            global_id2name = {}
            for p in self.svc.project_dict.values():
                # 内部环境变量
                env.setitem(
                    p.project_id,
                    "__importlib__",
                    EnvItem(
                        biz_types=EnvBizTypes.Env,
                        types="Any",
                        key="__importlib__",
                        value=importlib,
                    ),
                )

                # 全局变量
                global_list = self.svc.storage.global_list(p.project_id, p.project_mode, p.project_version)
                if len(global_list) > 0:
                    for g_v in global_list:
                        global_id2name[g_v.get("globalId")] = g_v.get("varName", "")
                        name = g_v.get("varName", None)
                        if not name:
                            continue

                        env.setitem(
                            p.project_id,
                            name,
                            EnvItem(
                                biz_types=EnvBizTypes.Global,
                                types=g_v.get("varType", "Any"),
                                key=name,
                                value=self.svc.params.parse_param(
                                    p.project_id,
                                    {
                                        "types": g_v.get("varType", "Any"),
                                        "name": g_v.get("varName", ""),
                                        "value": g_v.get("varValue", ""),
                                        "title": g_v.get(GLOBAL_PARAM_NAME_FORMAT.format(g_v.get("varName", ""))),
                                    },
                                    self.svc,
                                ),
                                ext={
                                    "globalId": g_v.get("globalId"),
                                    "varDescribe": g_v.get("varDescribe"),
                                },
                            ),
                        )
            self.svc.global_id2name = global_id2name

            # 全局事件
            event.raw_error_logger_handler = self.error_logger_handler
            event.raw_debug_handler = self.debug_handler

            # 日志2
            self.svc.report.info(
                ReportFlow(
                    log_type=ReportType.Flow,
                    status=ReportFlowStatus.INIT_SUCCESS,
                    msg_str=ReportFlowInitSuccess,
                )
            )
            return program

        try:
            return python_base_error(raw_project_init)()
        except Exception as e:
            # 主要是服务器错误和语法错误
            if isinstance(e, BaseException):
                error_str = e.code.message
            else:
                error_str = str(e)
            self.svc.report.error(
                ReportFlow(
                    log_type=ReportType.Flow,
                    status=ReportFlowStatus.TASK_ERROR,
                    result=ExecuteStatus.FAIL.value,
                    msg_str="{} {}".format(ReportFlowTaskError, error_str),
                    error_traceback=traceback.format_exc(),
                )
            )
            self.svc.storage.report_status_upload("fail", "{} {}".format(ReportFlowTaskError, error_str))
        return

    def __process_init__(self, program):
        if not program:
            return

        def raw_process_init():
            # 用户pip提前下载
            for p in self.svc.project_dict.values():
                pip_list = self.svc.storage.user_pip_list(p.project_id, p.project_mode, p.project_version)
                for pip in pip_list:
                    self.svc.atomic.download(
                        pip.get("packageName", ""),
                        pip.get("packageVersion", ""),
                        self.svc.cache_dir,
                        pip.get("mirror", ""),
                        bool(pip.get("packageVersion", "")),
                    )

            program.init(self.svc)

        try:
            python_base_error(raw_process_init)()
        except Exception as e:
            # 主要是pip下载错误
            self.svc.event_stop(True)
            if isinstance(e, BaseException):
                error_str = e.code.message
            else:
                error_str = str(e)
            self.svc.report.error(
                ReportFlow(
                    log_type=ReportType.Flow,
                    status=ReportFlowStatus.TASK_ERROR,
                    result=ExecuteStatus.FAIL.value,
                    msg_str="{} {}".format(ReportFlowTaskError, error_str),
                    error_traceback=traceback.format_exc(),
                )
            )
            self.svc.storage.report_status_upload("fail", "{} {}".format(ReportFlowTaskError, error_str))

    def __process_run__(self, program, env=None):
        if not program:
            return

        self.svc.report.info(
            ReportFlow(
                log_type=ReportType.Flow,
                status=ReportFlowStatus.TASK_START,
                msg_str=ReportFlowTaskStart,
            )
        )
        try:
            res = python_base_error(program.run)(self.svc, env)
        except CloseError as e:
            if str(e) == "kill":
                # 这个是异常关闭
                pass
            else:
                # 这个是主动关闭
                self.svc.report.info(
                    ReportFlow(
                        log_type=ReportType.Flow,
                        status=ReportFlowStatus.TASK_END,
                        result=ExecuteStatus.CANCEL.value,
                        msg_str=ReportFlowTaskEndUserClose,
                    )
                )
                self.svc.storage.report_status_upload("cancel", ReportFlowTaskEndUserClose)
            return
        except IgnoreException:
            self.svc.report.error(
                ReportFlow(
                    log_type=ReportType.Flow,
                    status=ReportFlowStatus.TASK_ERROR,
                    result=ExecuteStatus.FAIL.value,
                    msg_str="{}".format(ReportFlowTaskError),
                )
            )
            self.svc.storage.report_status_upload("fail", "{}".format(ReportFlowTaskError))
            return
        except Exception as e:
            # 原子能力执行错误
            if isinstance(e, BaseException):
                error_str = e.code.message
            else:
                error_str = str(e)
            self.svc.report.error(
                ReportFlow(
                    log_type=ReportType.Flow,
                    status=ReportFlowStatus.TASK_ERROR,
                    result=ExecuteStatus.FAIL.value,
                    msg_str="{} {}".format(ReportFlowTaskError, error_str),
                    error_traceback=traceback.format_exc(),
                )
            )
            self.svc.storage.report_status_upload("fail", "{} {}".format(ReportFlowTaskError, error_str))
            return
        self.svc.report.info(
            ReportFlow(
                log_type=ReportType.Flow,
                status=ReportFlowStatus.TASK_END,
                result=ExecuteStatus.SUCCESS.value,
                data=res,
                msg_str=ReportFlowTaskEnd,
            )
        )
        self.svc.storage.report_status_upload("success", "")
