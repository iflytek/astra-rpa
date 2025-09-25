import os
from typing import Any


class CompressCore:
    @staticmethod
    def compress(items: list, file_name: str = "", dest_path: str = "", pwd: str = "") -> str:
        import pyzipper

        if not file_name.endswith(".zip"):
            file_name += ".zip"

        try:
            zip_path = os.path.join(dest_path, file_name)
            if pwd:
                with pyzipper.AESZipFile(
                    zip_path,
                    "w",
                    compression=pyzipper.ZIP_DEFLATED,
                    encryption=pyzipper.WZ_AES,
                ) as zip_file:
                    zip_file.setpassword(pwd.encode("utf-8"))
                    CompressCore.__add_items_to_zip__(zip_file, items)
            else:
                with pyzipper.ZipFile(zip_path, "w", compression=pyzipper.ZIP_DEFLATED) as zip_file:
                    CompressCore.__add_items_to_zip__(zip_file, items)
            return os.path.abspath(zip_path)
        except Exception as e:
            raise ValueError("压缩失败：{}".format(e))

    @staticmethod
    def __add_items_to_zip__(zip_file, items: list) -> None:
        """
        向zip文件中写入待压缩文件
        """
        for item in items:
            if os.path.isfile(item):
                zip_file.write(item, os.path.basename(item))
            elif os.path.isdir(item):
                folder_name = os.path.basename(item) if len(items) > 1 else ""
                for root, dirs, files in os.walk(item):
                    for file in files:
                        abs_file_path = os.path.join(root, file)
                        relative_file_path = os.path.relpath(abs_file_path, item)
                        zip_file.write(abs_file_path, os.path.join(folder_name, relative_file_path))

    @staticmethod
    def __support_gbk__(zip_file):
        """
        处理ZIP文件中可能存在的中文文件名乱码的问题
        """
        name_to_info = zip_file.NameToInfo
        for name, info in name_to_info.copy().items():
            try:
                real_name = name.encode("cp437").decode("gbk")
            except:
                real_name = name
            if real_name != name:
                info.filename = real_name
                del name_to_info[name]
                name_to_info[real_name] = info
        return zip_file

    @staticmethod
    def uncompress(source_path: str = "", dest_path: str = "", pwd: str = "") -> Any:
        if source_path.endswith(".zip"):
            import pyzipper

            with pyzipper.AESZipFile(source_path) as handler:
                handler = CompressCore.__support_gbk__(handler)
                if pwd:
                    handler.pwd = pwd.encode("utf-8")
                handler.extractall(path=dest_path)
        elif source_path.endswith(".7z"):
            import py7zr

            with py7zr.SevenZipFile(source_path, mode="r", password=pwd) as handler:
                handler.extractall(path=dest_path)
        else:
            raise ValueError("不支持的解压缩类型")
        return os.path.abspath(dest_path)
