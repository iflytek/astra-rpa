import os
import re
import sys

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpasystem import *
from rpasystem.error import *

if sys.platform == "win32":
    from rpasystem.core.process_core import ProcessCoreWin

    ProcessCore = ProcessCoreWin
else:
    from rpasystem.core.process_core import ProcessCoreLinux

    ProcessCore = ProcessCoreLinux


class Process:
    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param(
                "command",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                required=True,
            ),
            atomicMg.param("params", types="Str", level=AtomicLevel.ADVANCED.value, required=False),
            atomicMg.param("cmd_type", required=False),
            atomicMg.param(
                "work_dir",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                level=AtomicLevel.ADVANCED.value,
                required=False,
            ),
            atomicMg.param(
                "wait_time",
                types="Int",
                dynamics=[
                    DynamicsItem(
                        key="$this.wait_time.show",
                        expression="return $this.run_type.value == '{}'".format(RunType.COMPLETE.value),
                    )
                ],
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("process_out", types="Any"),
        ],
    )
    def run_command(
        command: str = "",
        cmd_type: CmdType = CmdType.NORMAL,
        run_type: RunType = RunType.CONTINUE,
        params: str = None,
        work_dir: str = "",
        wait_time: int = 60,
    ):
        """
        运行cmd命令或执行.exe文件
        """
        # 在Windows上，如果命令包含路径，需要正确处理
        if os.path.isfile(command):
            # 如果是文件路径，使用引号包围路径
            command = f'"{command}"'
        elif " " in command and not command.startswith('"'):
            # 如果命令包含空格且没有引号，添加引号
            command = f'"{command}"'

        if params:
            command = f"{command} {''.join(params)}"
        try:
            if cmd_type == CmdType.NORMAL:
                process = ProcessCore.run_cmd(command, cwd=work_dir)
            elif cmd_type == CmdType.ADMIN:
                process = ProcessCore.run_cmd_admin(command, cwd=work_dir)
            else:
                raise NotImplementedError()

            if run_type == RunType.CONTINUE:
                return True
            elif run_type == RunType.COMPLETE:
                process.wait(wait_time)
            else:
                raise NotImplementedError()
        except Exception as e:
            raise BaseException(CMD_ERROR_FORMAT.format(command, e), "CMD命令执行失败")
        return True

    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param(
                "process_name",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                required=True,
            ),
            atomicMg.param("search_type", required=False),
            atomicMg.param("pid_type", required=False),
        ],
        outputList=[
            atomicMg.param("match_proces_pid", types="Any"),
        ],
    )
    def get_pid(
        process_name: str = "",
        search_type: SearchType = SearchType.EXACT,
        pid_type: PidType = PidType.ALL,
    ):
        """
        获取与输入名称匹配的进程PID,并保存至输出变量
        """
        import psutil

        if not process_name:
            raise BaseException(
                MSG_EMPTY_FORMAT.format(process_name),
                "待匹配名称输入为空，请检查输入信息！",
            )
        match_proces_pid = []
        for proc in ProcessCore.get_pid_list():
            try:
                name = proc.info["name"]
                if search_type == SearchType.EXACT and process_name == name:
                    matched = True
                elif search_type == SearchType.FUZZY and process_name in name:
                    matched = True
                elif search_type == SearchType.REGEX and re.search(process_name, name):
                    matched = True
                else:
                    matched = False

                if matched:
                    if pid_type == PidType.ONE:
                        return proc.pid
                    elif pid_type == PidType.ALL:
                        match_proces_pid.append(proc.pid)
                    else:
                        raise NotImplementedError()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return match_proces_pid

    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param("termination_type", required=False),
            atomicMg.param(
                "pid",
                types="Any",
                dynamics=[
                    DynamicsItem(
                        key="$this.pid.show",
                        expression="return $this.termination_type.value == '{}'".format(TerminationType.PID.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "process_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.process_name.show",
                        expression="return $this.termination_type.value == '{}'".format(TerminationType.NAME.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "time_out",
                types="Int",
                level=AtomicLevel.ADVANCED.value,
                required=False,
            ),
        ],
        outputList=[atomicMg.param("termination_process", types="Bool")],
    )
    def terminate_process(
        termination_type: TerminationType = TerminationType.PID,
        pid=None,
        process_name: str = "",
        time_out: int = 5,
    ):
        termination_process = False
        if termination_type == TerminationType.PID:
            if isinstance(pid, list):
                for p in pid:
                    ProcessCore.terminate_pid(p, wait_time=time_out)
            elif isinstance(pid, int):
                ProcessCore.terminate_pid(pid, wait_time=time_out)
            else:
                raise NotImplementedError("输入PID值错误，请检查输入类型")
            termination_process = True
        elif termination_type == TerminationType.NAME:
            for proc in ProcessCore.get_pid_list():
                if proc.info["name"] == process_name:
                    ProcessCore.terminate_pid(proc.pid, wait_time=time_out)
            termination_process = True
        return termination_process
