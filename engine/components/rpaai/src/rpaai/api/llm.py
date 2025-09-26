import json
from typing import Any

import requests
import sseclient

from rpaai.error import *

API_URL = "http://127.0.0.1:8003/api/rpa-ai-service/v1/chat/completions"
PROMPT_URL = "http://127.0.0.1:8003/api/rpa-ai-service/v1/chat/prompt"


def chat_streamable(messages: Any, model: str = "deepseek-v3-0324"):
    """
    调用远端大模型

    :param
    messages: 历史问题
    model: 模型id

    - example
        inputs = [
            {"role": "assistant", "content": "请模仿李白的口吻"},
            {"role": "user", "content": "写一首咏鹅诗"}
        ]

        outputs = {"content":"笔","reasoning_content":null}

    """
    chat_json = {"messages": messages, "model": model, "stream": True}

    response = requests.post(API_URL, json=chat_json)
    if response.status_code == 200:
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data and event.data != "[DONE]":
                response_json = json.loads(event.data)
                if response_json.get("choices"):
                    yield response_json["choices"][0]["delta"]["content"]
    else:
        raise BaseException(LLM_NO_RESPONSE_ERROR.format(response), "")


def chat_normal(user_input, system_input="", model="deepseek-v3-0324"):
    # 构建请求的 payload
    data = {
        "model": model,  # 选择大模型，替换为实际模型标识
        "messages": [
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_input},
        ],
    }

    try:
        # 发送 API 请求
        response = requests.post(API_URL, data=json.dumps(data))
        response.raise_for_status()  # 检查请求是否成功

        # 返回模型生成的回复
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except KeyError:
        print("响应格式不正确")
        return None


def chat_prompt(prompt_type, params, model="deepseek-v3-0324"):
    # 构建请求的 payload
    data = {
        # 'model': model,  # 选择大模型，替换为实际模型标识
        "prompt_type": prompt_type,
        "params": params,
    }

    try:
        # 发送 API 请求
        response = requests.post(PROMPT_URL, data=json.dumps(data))
        response.raise_for_status()  # 检查请求是否成功

        # 返回模型生成的回复
        response_json = response.json()
        return response_json["data"]

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except KeyError:
        print("响应格式不正确")
        return None


if __name__ == "__main__":
    inputs = [
        {"role": "assistant", "content": "请模仿李白的口吻"},
        {"role": "user", "content": "写一首咏鹅诗"},
    ]

    # inputs = [
    #     {'role': 'assistant', 'content': 'download from the releases pageadd -javaagent:/absolute/path/to/ja-netfilter.jar argument (Change to youractual path)add as an argument of the java command. eg:java -javaagent:/absolute/path/to/ja-netfilter.jar -jar executable_jar_file.jarsome apps support the JVM Options file, you can add as a line of theJVM Options file.WARNING: DO NOT put some unnecessary whitespace characters!or execute java -jar /path/to/ja-netfilter.jar to use attach mode.for Java 17 you have to add at least these JVM Options:--add-opens=java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED--add-opens=java.base/jdk.internal.org.objectweb.asm.tree=ALL-UNNAMEDedit your plugin conﬁg ﬁles: ${lower plugin name}.conf ﬁle in the config dir whereja-netfilter.jar is located.the config, logs and plugins directories can be speciﬁed through the javaagent args.eg: -javaagent:/path/to/ja-netfilter.jar=appName, your conﬁg, logs and pluginsdirectories will be config-appname, logs-appname and plugins-appname.if no javaagent args, they default to config, logs and plugins.this mechanism will avoid extraneous and bloated config, logs and plugins.run your java application and enjoy~ja-netﬁlter 2022.2.0A javaagent frameworkUsage\nConﬁg ﬁle format\n[ABC]# for the specified section name# for example[URL]EQUAL,https://someurl[DNS]EQUAL,somedomain# EQUAL       Use `equals` to compare# EQUAL_IC    Use `equals` to compare, ignore case# KEYWORD     Use `contains` to compare# KEYWORD_IC  Use `contains` to compare, ignore case# PREFIX      Use `startsWith` to compare# PREFIX_IC   Use `startsWith` to compare, ignore case# SUFFIX      Use `endsWith` to compare# SUFFIX_IC   Use `endsWith` to compare, ignore case# REGEXP      Use regular expressions to matchthe ja-netfilter will NOT output debugging information by defaultadd environment variable JANF_DEBUG=1 (log level) and start to enable itor add system property -Djanf.debug=1 (log level) to enable itlog level: NONE=0, DEBUG=1, INFO=2, WARN=3, ERROR=4the ja-netfilter will output debugging information to the console by defaultadd environment variable JANF_OUTPUT=value and start to change output mediumor add system property -Djanf.output=value to change output mediumoutput medium value: [NONE=0, CONSOLE=1, FILE=2, CONSOLE+FILE=3,WITH_PID=4]eg: console + file + pid file name = 1 + 2 + 4 = 7, so the -Djanf.output=7for developer:view the scaffold project written for the plugin systemcompile your plugin and publish itjust use your imagination~for user:download the jar ﬁle of the pluginput it in the subdirectory called plugins where the ja-netﬁlter.jar ﬁle is locatedDebug infoDebug outputPlugin system\nenjoy the new capabilities brought by the pluginif the ﬁle sufﬁx is .disabled.jar, the plugin will be disabled'},
    #     {'role': 'user', 'content': '你是什么大模型'},
    #
    # ]

    s = []
    r = []
    for i in chat_streamable(inputs):
        if i.get("content"):
            s.append(i.get("content"))
        if i.get("reasoning_content"):
            r.append(i.get("reasoning_content"))
    print("".join(r))
    print("".join(s))
