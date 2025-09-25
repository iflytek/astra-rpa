import re
import subprocess
import sys
from enum import Enum

import pyperclip


class Base64CodeType(Enum):
    STRING = "string"
    PICTURE = "picture"


class Clipboard:
    @staticmethod
    def paste_str_clip() -> str:
        """
        获取剪切板
        :return:
        """
        return pyperclip.paste()

    @staticmethod
    def paste_html_clip() -> str:
        if sys.platform != "win32":
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o", "-t", "text/html"],
                capture_output=True,
                text=True,
            )
            html_data = result.stdout
            return html_data

        import win32clipboard as cp

        html_data = ""
        cp.OpenClipboard()
        try:
            CF_HTML = cp.RegisterClipboardFormat("HTML Format")
            if cp.IsClipboardFormatAvailable(CF_HTML):
                html_data = cp.GetClipboardData(CF_HTML)
        except:
            pass
        finally:
            cp.CloseClipboard()

        if html_data:
            html_fragment = Clipboard._extract_html_fragment(html_data)
            if html_fragment:
                # 正则表达式模式，匹配 src=" 和 " 之间的内容
                pattern = r'src="file:///(.*?\.(?:jpg|png|gif))"'
                # 使用 re.findall 查找所有匹配项
                matches = re.findall(pattern, html_fragment)
                for match in matches:
                    base64_str = Clipboard._base64_encode(Base64CodeType.PICTURE, "", match)
                    html_fragment = html_fragment.replace(r"file:///" + match, base64_str)
                return html_fragment
            else:
                return html_data
        else:
            # 非HTML格式返回文本
            return Clipboard.paste_str_clip()

    @staticmethod
    def _extract_html_fragment(html_clipboard_data):
        html_clipboard_str = html_clipboard_data.decode("utf-8")

        start_marker = "<!--StartFragment-->"
        end_marker = "<!--EndFragment-->"

        start_index = html_clipboard_str.find(start_marker)
        end_index = html_clipboard_str.find(end_marker)

        if start_index == -1 or end_index == -1:
            # 使用正则表达式进行匹配
            # 一般小的複製會是這種形式
            match_start = re.search(r"StartHTML:(\d+)\r", html_clipboard_str).group(1)
            match_end = re.search(r"EndHTML:(\d+)\r", html_clipboard_str).group(1)
            return html_clipboard_str[int(match_start) : int(match_end)]

        start_offset = start_index + len(start_marker)
        end_offset = end_index
        # Extract the HTML fragment using the offsets
        html_fragment = html_clipboard_str[start_offset:end_offset]
        return html_fragment

    @staticmethod
    def _base64_encode(
        encode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ) -> str:
        import base64

        if file_path:
            with open(file_path, "rb") as file:
                input_content = file.read()
        else:
            input_content = string_data.encode("utf-8")
        base64_encoded = base64.b64encode(input_content)
        base64_encode_result = base64_encoded.decode("utf-8")
        if encode_type == Base64CodeType.PICTURE:
            base64_encode_result = "data:image/png;base64," + base64_encode_result
        return base64_encode_result
