import copy
import json
import os
import shutil
import subprocess
import sys
import time

from rpaai import LLMModelTypes
from rpaatomic import AtomicFormType, AtomicFormTypeMeta
from rpatools.tools import RpaTools

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(os.path.dirname(os.path.abspath(__file__)))

from rpaai.api.llm import chat_normal, chat_streamable
from rpaai.error import *
from rpaai.prompt.g_chat import prompt_generate_question
from rpaai.utils.extract import FileExtractor
from rpaai.utils.str import replace_keyword
from rpaatomic.atomic import atomicMg
from rpaframe.logger.logger import logger


class ChatAI:
    @staticmethod
    @atomicMg.atomic("ChatAI", outputList=[atomicMg.param("single_chat_res", types="Str")])
    def single_turn_chat(query: str, model: LLMModelTypes = LLMModelTypes.DS_CHAT) -> str:
        """
        单轮对话方法
        Args:
            - query(str): 用户问题
        Return:
            `str`, 大模型生成的答案
        """

        return chat_normal(user_input=query, system_input="", model=model.value)

    @staticmethod
    @atomicMg.atomic("ChatAI", outputList=[atomicMg.param("chat_res", types="Dict")])
    def chat(
        is_save: bool,
        title: str,
        max_turns: int,
        model: LLMModelTypes = LLMModelTypes.DS_CHAT,
    ) -> dict:
        """
        多轮对话方法
        Args:
            - is_save(bool): 用于判断是否需要保存最后的导出对话
            - title(title): 标题名称
            - max_turns(int): 最大问答的轮数
        Return:
            `dict`, 选择导出的记录
        """

        # 拉起窗口
        exe_path = RpaTools.get_window_dir()
        args = [
            exe_path,
            f"--url=tauri://localhost/multichat.html?max_turns={str(max_turns)}&is_save={str(int(is_save))}&title={title}&model={model.value}",
            f"--height=600",
        ]
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        # 数据输出
        save_dict = {}
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if not output:
                continue
            save_str = output.strip()
            try:
                save_dict = json.loads(save_str)
            except Exception as e:
                logger.error(f"save_dict：{save_str}")
                pass

        try:
            time.sleep(1)
            process.kill()
        except Exception as e:
            pass

        return save_dict

    @staticmethod
    @atomicMg.atomic(
        "ChatAI",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[atomicMg.param("knowledge_chat_res", types="Dict")],
    )
    def knowledge_chat(
        file_path: str,
        is_save: bool = False,
        max_turns: int = 20,
    ):
        """
        知识库问答
        Args:
            - file_path(str): 文件路径
            - is_save(bool): 用于判断是否需要保存最后的导出对话
            - max_turns(int): 最大问答的轮数

        Return:
            `dict`, 选择导出的记录
        """
        _, extension = os.path.splitext(file_path)

        # 解析文件
        if "pdf" in extension.lower():
            file_content = FileExtractor.extract_pdf(file_path)
        elif "docx" in extension.lower():
            file_content = FileExtractor.extract_docx(file_path)
        else:
            raise NotImplementedError(f"Not support file type：{extension}")

        # 提出三个问题
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_generate_question),
            input_keys=[{"keyword": "text", "text": file_content[:18000]}],
        )
        content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")
        try:
            import ast

            output = ast.literal_eval(s_content)
        except Exception:
            output = [
                "这篇文本的主题是什么？",
                "文本中提到了哪些关键信息?",
                "文本提到了哪些具体的结果？",
            ]

        # 拷贝相关文件（在该路径下，前端有读取的权限）
        word_dir = os.path.join("cache", "chatData")
        # # 拷贝相关文件（在该路径下，前端有读取的权限）
        # word_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "iflyrpa", "cache", "chatData")
        dest_file = os.path.join(word_dir, os.path.basename(file_path))
        if not os.path.exists(word_dir):
            os.makedirs(word_dir)
        if os.path.exists(dest_file):
            os.remove(dest_file)
        shutil.copy2(file_path, dest_file)

        # 拉起窗口
        exe_path = RpaTools.get_window_dir()
        args = [
            exe_path,
            f"--url=tauri://localhost/multichat.html?max_turns={str(max_turns)}&is_save={str(int(is_save))}&questions={'$-$'.join(output)}&file_path={file_path}",
            f"--content={file_content[:5000]}",
            "--height=700",
        ]
        # args = [exe_path, f"--url=https://tauri.localhost/multichat.html?max_turns={str(max_turns)}&is_save={str(int(is_save))}&questions={'$-$'.join(output)}&file_path={file_path}", f"--content={file_content[:5000]}", "--height=700"]
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        # 数据输出
        save_dict = {}
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if not output:
                continue

            if output == "" and process.poll() is not None:
                break
            if not output:
                continue
            save_str = output.strip()
            try:
                save_dict = json.loads(save_str)
            except Exception:
                pass

        # 文件清空
        if os.path.exists(dest_file):
            os.remove(dest_file)

        try:
            time.sleep(1)
            process.kill()
        except Exception:
            pass
            try:
                save_dict = json.loads(save_str)
                print(f"save_dict：{save_dict}")
            except Exception as error:
                pass

        if os.path.exists(dest_file):
            os.remove(dest_file)

        try:
            time.sleep(1)
            process.kill()
        except Exception:
            pass

        return save_dict

    @staticmethod
    def streamable_response(inputs: list):
        content = []
        reason = []
        for i in chat_streamable(inputs):
            if i.get("content"):
                content.append(i.get("content"))
            if i.get("reasoning_content"):
                reason.append(i.get("reasoning_content"))
        return content, reason
