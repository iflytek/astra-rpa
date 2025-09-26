# encoding: UTF-8

import copy

from rpaatomic.atomic import atomicMg

from rpaai.chat import ChatAI
from rpaai.prompt.g_document import (
    prompt_sentence_extend,
    prompt_sentence_reduce,
    prompt_theme_extend,
)
from rpaai.utils.str import replace_keyword


class DocumentAI:
    @staticmethod
    @atomicMg.atomic("DocumentAI", outputList=[atomicMg.param("theme_expand_res", types="Str")])
    def theme_expand(text: str) -> str:
        # 生成提示词
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_theme_extend),
            input_keys=[{"keyword": "theme", "text": text}],
        )

        # 向大模型发送请求
        content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")

        return s_content

    @staticmethod
    @atomicMg.atomic("DocumentAI", outputList=[atomicMg.param("sentence_expand_res", types="Str")])
    def sentence_expand(text: str):
        """
        段落扩写

        :param text: 段落

        :return:
            `str`, 扩写结果
        """

        # 生成提示词
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_sentence_extend),
            input_keys=[{"keyword": "paragraph", "text": text}],
        )

        # 向大模型发送请求
        content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")

        return s_content

    @staticmethod
    @atomicMg.atomic("DocumentAI", outputList=[atomicMg.param("sentence_reduce_res", types="Str")])
    def sentence_reduce(text: str):
        """
        段落缩写

        :param text: 段落

        :return:
            `str`, 扩写结果
        """

        # 生成提示词
        inputs = replace_keyword(
            prompts=copy.deepcopy(prompt_sentence_reduce),
            input_keys=[{"keyword": "paragraph", "text": text}],
        )

        # 向大模型发送请求
        content, _ = ChatAI.streamable_response(inputs)
        s_content = "".join(content).replace("，", ",")

        return s_content
