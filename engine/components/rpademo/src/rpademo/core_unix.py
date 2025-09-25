import os
import subprocess

from rpademo.core import IDemoCore


class DemoCore(IDemoCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return "linux {}".format(msg)

    @staticmethod
    def create_and_open_txt(file_path: str, content: str = "helloworld") -> str:
        """
        在Unix系统中创建txt文件并写入内容，然后打开文件
        """
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # 创建并写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # 使用系统默认程序打开文件
            try:
                # 尝试使用xdg-open (Linux)
                subprocess.run(["xdg-open", file_path], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    # 尝试使用open (macOS)
                    subprocess.run(["open", file_path], check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # 如果都失败了，至少文件已经创建成功
                    return f"成功创建文件 {file_path} 并写入内容: {content}，但无法自动打开文件"

            return f"成功创建文件 {file_path} 并写入内容: {content}"

        except Exception as e:
            return f"创建文件失败: {str(e)}"
