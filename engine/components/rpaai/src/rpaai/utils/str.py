import os
import sys


def replace_keyword(prompts: list, input_keys: list) -> list:
    """
    批量替换关键词
    :param input_keys: [{"keyword": "question", "text": "Your replacement keyword"}]
    :param prompts: Template will be replaced

    :return {"role": "System", "content": "问题是：{本月H6国潮版在全国各地的经销商库存总量是多少?}"}
    """
    for input_key in input_keys:
        for ind, prompt in enumerate(prompts):
            keyword = "{" + f"{input_key['keyword']}" + "}"
            if keyword in prompt["content"]:
                prompts[ind]["content"] = prompt["content"].replace(keyword, input_key["text"])
    return prompts


def platform_python_path(parent_dir: str):
    if sys.platform == "win32":
        path = os.path.join(parent_dir, r"python.exe")
    else:
        path = os.path.join(parent_dir, "bin", "python3.7")
    return path
