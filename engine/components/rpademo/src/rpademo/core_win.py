import os

from rpademo.src.rpademo.core import IDemoCore


class DemoCore(IDemoCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return "win {}".format(msg)

    @staticmethod
    def create_and_open_txt(file_path: str, content: str = "helloworld") -> str:
        """
        在Windows系统中创建txt文件并写入内容，然后打开文件
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
            os.startfile(file_path)

            return f"成功创建文件 {file_path} 并写入内容: {content}"

        except Exception as e:
            return f"创建文件失败: {str(e)}"
