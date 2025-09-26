import ftplib
import os.path

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg

from rpanetwork import FileExistenceType, FileType, ListType, StateType
from rpanetwork.core_ftp import FtpCore
from rpanetwork.error import *
from rpanetwork.utils import (
    file_is_exist,
    folder_is_exist,
    generate_local_name,
    get_exist_files,
    get_file_list,
)


class FTP:
    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("host", types="Str", required=True),
            atomicMg.param("port", types="Int", required=True),
            atomicMg.param("name", types="Str", required=False),
            atomicMg.param("password", types="Str", required=False),
        ],
        outputList=[atomicMg.param("ftp_instance", types="Str")],
    )
    def ftp_create(host: str, port: int, name: str, password: str):
        ftp_instance = FtpCore.create_ftp()
        try:
            FtpCore.ftp_connection(ftp_instance, host, port)
        except Exception as e:
            raise BaseException(FTP_CONNECTION_FORMAT.format(host, port), "连接到FTP服务器失败")

        if name and password:
            try:
                FtpCore.ftp_login(ftp_instance, name, password)
            except Exception as e:
                raise BaseException(FTP_LOGIN_FORMAT.format(name, password), "登录到FTP服务器失败")

        return ftp_instance

    @staticmethod
    @atomicMg.atomic(
        "Network",
        outputList=[
            atomicMg.param("close_ftp", types="Bool"),
        ],
    )
    def ftp_close(ftp_instance: ftplib.FTP):
        try:
            FtpCore.close_ftp(ftp_instance)
            return True
        except Exception as e:
            raise BaseException(FTP_CLOSE_FORMAT.format(e), "FTP连接关闭失败")

    @staticmethod
    @atomicMg.atomic(
        "Network",
        outputList=[
            atomicMg.param("get_work_dir", types="Str"),
        ],
    )
    def get_work_dir(ftp_instance: ftplib.FTP):
        try:
            get_work_dir = FtpCore.get_working_dir(ftp_instance)
        except Exception as e:
            raise BaseException(FTP_STATUS_FORMAT.format(e), "{e}")
        return get_work_dir

    @staticmethod
    @atomicMg.atomic(
        "Network",
        outputList=[
            atomicMg.param("change_work_dir", types="Str"),
        ],
    )
    def change_working_dir(ftp_instance: ftplib.FTP, new_work_dir: str):
        try:
            FtpCore.change_working_dir(ftp_instance, new_work_dir)
            change_work_dir = FtpCore.get_working_dir(ftp_instance)
            return change_work_dir
        except Exception as e:
            raise BaseException(FTP_STATUS_FORMAT.format(e), "{e}")

    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("ftp_instance", types="Str"),
            atomicMg.param("folder_name", types="Str"),
            atomicMg.param(
                "exist_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("new_folder", types="Str"),
        ],
    )
    def create_folder(
        ftp_instance: ftplib.FTP,
        folder_name: str,
        exist_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        """
        创建文件夹
        :param ftp_instance: FTP连接对象
        :param folder_name: 文件夹名称
        :param exist_type: 文件夹存在时
        :return: 新建文件夹路径
        """
        get_list = FtpCore.get_nlst(ftp_instance)
        if folder_name in get_list:
            if exist_type == FileExistenceType.RENAME:
                folder_name = FtpCore.generate_name(ftp_instance, folder_name)
            elif exist_type == FileExistenceType.CANCEL:
                return FtpCore.get_path(ftp_instance, folder_name)
            elif exist_type == FileExistenceType.OVERWRITE:
                FtpCore.ftp_delete_dir(ftp_instance, folder_name)
            else:
                raise NotImplementedError

        try:
            new_folder = FtpCore.create_dir(ftp_instance, folder_name)
        except Exception as e:
            raise BaseException(FTP_CREATE_FORMAT.format(e), "文件夹创建失败：{}".format(e))

        return new_folder

    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("file_type", required=False),
        ],
        outputList=[
            atomicMg.param("get_ftp_list", types="Dict"),
        ],
    )
    def get_ftp_list(ftp_instance: ftplib.FTP, file_type: ListType = ListType.FILE):
        """
        获取工作目录下文件/文件夹
        :param ftp_instance: FTP连接对象
        :param file_type: 获取类型
        :return: 获取内容
        """
        file_structure = {"files": [], "folders": []}
        try:
            FtpCore.get_working_dir(ftp_instance)
        except Exception as e:
            raise BaseException(FTP_STATUS_FORMAT.format(e), "{e}")

        try:
            list_file = FtpCore.get_nlst(ftp_instance)
            for item in list_file:
                if FtpCore.is_dir(ftp_instance, item):
                    file_structure["folders"].append(item)
                else:
                    file_structure["files"].append(item)

            if file_type == ListType.FILE:
                return file_structure["files"]
            elif file_type == ListType.FOLDER:
                return file_structure["folders"]
            elif file_type == ListType.ALL:
                return file_structure
            else:
                raise NotImplementedError()
        except Exception as e:
            raise BaseException(FTP_STATUS_FORMAT.format(e), "{e}")

    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("ftp_instance", types="Str", required=True),
            atomicMg.param("file_type", required=False),
            atomicMg.param(
                "cur_file_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.cur_file_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FILE.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "new_file_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.new_file_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FILE.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "cur_folder_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.cur_folder_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FOLDER.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "new_folder_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.new_folder_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FOLDER.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "exist_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("rename_ftp_path", types="Str"),
        ],
    )
    def ftp_rename(
        ftp_instance: ftplib.FTP,
        file_type: FileType = FileType.FILE,
        cur_file_name: str = "",
        new_file_name: str = "",
        cur_folder_name: str = "",
        new_folder_name: str = "",
        exist_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        """
        对FTP服务器上的文件/文件夹重命名
        :param ftp_instance: 连接的FTP服务器
        :param file_type: 重命名类型 文件/文件夹
        :param cur_file_name:  原文件名称
        :param new_file_name:  新文件名称（不需扩展名）
        :param cur_folder_name:  原文件夹名称
        :param new_folder_name:  新文件夹名称
        :param exist_type:  文件存在时
        :return: 重命名后文件路径
        """

        exist_file = FtpCore.get_nlst(ftp_instance)

        if file_type == FileType.FILE:
            if cur_file_name not in exist_file:
                raise BaseException(FILE_EXIST_FORMAT.format(cur_file_name), "待重命名文件不存在")

            file_ext = os.path.splitext(cur_file_name)[1]
            if not file_ext:
                raise BaseException(
                    FILE_NAME_FORMAT.format(cur_file_name),
                    "输入文件名扩展名缺失，请检查输入内容",
                )

            new_file_name = new_file_name + file_ext
            if new_file_name in exist_file:
                if exist_type == FileExistenceType.CANCEL:
                    return FtpCore.get_path(ftp_instance, cur_file_name)
                elif exist_type == FileExistenceType.OVERWRITE:
                    FtpCore.ftp_delete_file(ftp_instance, new_file_name)
                elif exist_type == FileExistenceType.RENAME:
                    new_file_name = FtpCore.generate_name(ftp_instance, new_file_name)
                else:
                    raise NotImplementedError()
            try:
                FtpCore.ftp_rename(ftp_instance, cur_file_name, new_file_name)
                return FtpCore.get_path(ftp_instance, new_file_name)
            except Exception as e:
                raise BaseException(FTP_RENAME_FORMAT.format(e), "FTP文件重命名失败")

        elif file_type == FileType.FOLDER:
            if cur_folder_name not in exist_file:
                raise BaseException(FOLDER_EXIST_FORMAT.format(cur_folder_name), "待重命名文件夹不存在")

            if not FtpCore.is_dir(ftp_instance, cur_folder_name):
                raise BaseException(
                    FILE_NAME_FORMAT.format(cur_folder_name),
                    "待重命名内容非文件夹，请检查输入信息",
                )

            if new_folder_name in exist_file:
                if exist_type == FileExistenceType.CANCEL:
                    return FtpCore.get_path(ftp_instance, cur_folder_name)
                elif exist_type == FileExistenceType.OVERWRITE:
                    FtpCore.ftp_delete_dir(ftp_instance, new_folder_name)
                elif exist_type == FileExistenceType.RENAME:
                    new_folder_name = FtpCore.generate_name(ftp_instance, new_folder_name)
                else:
                    raise NotImplementedError()
            try:
                FtpCore.ftp_rename(ftp_instance, cur_file_name, new_folder_name)
                return FtpCore.get_path(ftp_instance, new_folder_name)
            except Exception as e:
                raise BaseException(FTP_RENAME_FORMAT.format(e), "FTP文件重命名失败")

    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "files"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FILE.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "folder_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.folder_path.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FOLDER.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param("file_type", required=False),
            atomicMg.param("ftp_pwd", types="Str", required=False),
            atomicMg.param(
                "exist_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("upload_ftp_list", types="List"),
        ],
    )
    def ftp_upload(
        ftp_instance: ftplib.FTP,
        file_type: FileType = FileType.FILE,
        ftp_pwd: str = "",
        file_path: str = "",
        folder_path: str = "",
        exist_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        if ftp_pwd:
            if not FtpCore.is_dir(ftp_instance, ftp_pwd):
                if not FtpCore.create_dir(ftp_instance, ftp_pwd):
                    raise BaseException(
                        FTP_CREATE_FORMAT.format(ftp_pwd),
                        "指定{}目录创建失败，请检查FTP连接或目录名称，请勿使用中文目录".format(ftp_pwd),
                    )
            FtpCore.change_working_dir(ftp_instance, ftp_pwd)

        dst_list = FtpCore.get_nlst(ftp_instance)
        upload_ftp_list = []

        if file_type == FileType.FILE:
            file_list = get_file_list(file_path)
            for file in file_list:
                if not file_is_exist(file):
                    raise BaseException(FILE_EXIST_FORMAT.format(file), "待上传文件不存在或格式错误")

                file_name = os.path.basename(file)

                if file_name in dst_list:
                    if exist_type == FileExistenceType.CANCEL:
                        return FtpCore.get_path(ftp_instance, file_name)
                    elif exist_type == FileExistenceType.OVERWRITE:
                        FtpCore.ftp_delete_file(ftp_instance, file_name)
                    elif exist_type == FileExistenceType.RENAME:
                        file_name = FtpCore.generate_name(ftp_instance, file_name)
                    else:
                        raise NotImplementedError()
                try:
                    dst_path = FtpCore.ftp_upload_file(ftp_instance, file, file_name)
                except Exception as e:
                    raise BaseException(FTP_UPLOAD_FORMAT.format(file), "文件上传失败，请检查FTP连接")
                upload_ftp_list.append(dst_path)

        elif file_type == FileType.FOLDER:
            folder_list = get_file_list(folder_path)
            for folder in folder_list:
                if not folder_is_exist(folder):
                    raise BaseException(FOLDER_EXIST_FORMAT.format(folder), "待上传文件夹不存在")

                folder_name = os.path.basename(folder)
                if folder_name in dst_list:
                    if exist_type == FileExistenceType.CANCEL:
                        return FtpCore.get_path(ftp_instance, folder_name)
                    elif exist_type == FileExistenceType.OVERWRITE:
                        FtpCore.ftp_delete_dir(ftp_instance, folder_name)
                    elif exist_type == FileExistenceType.RENAME:
                        folder_name = FtpCore.generate_name(ftp_instance, folder_name)
                    else:
                        raise NotImplementedError()
                try:
                    dst_path = FtpCore.ftp_upload_dir(ftp_instance, folder, folder_name)
                except Exception as e:
                    raise BaseException(FTP_UPLOAD_FORMAT.format(folder), "文件上传失败，请检查FTP连接")
                upload_ftp_list.append(dst_path)
        else:
            raise NotImplementedError()

        return upload_ftp_list

    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("file_type", required=False),
            atomicMg.param(
                "download_file_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.download_file_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FILE.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "download_folder_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.download_folder_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FOLDER.value),
                    )
                ],
            ),
            atomicMg.param(
                "dst_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                required=True,
            ),
            atomicMg.param("state_type", required=False),
            atomicMg.param(
                "exist_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("download_ftp_path", types="List"),
        ],
    )
    def ftp_download(
        ftp_instance: ftplib.FTP,
        file_type: FileType = FileType.FILE,
        download_file_name: str = "",
        download_folder_name: str = "",
        dst_path: str = "",
        state_type: StateType = StateType.CREATE,
        exist_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        """
        从指定FTP服务器上下载文件/文件夹
        :param ftp_instance: FTP连接对象
        :param file_type: 下载对象  文件/文件夹
        :param download_file_name: 下载文件名称,多个文件名之间使用,隔开
        :param download_folder_name:  下载文件夹名称,多个文件夹名称之间使用,隔开
        :param dst_path:    本地目录
        :param state_type:  目录不存在时   创建/提示并报错
        :param exist_type:   文件/文件夹存在时   覆盖/重命名/跳过
        :return: 下载后文件/文件夹路径列表
        """
        if not folder_is_exist(dst_path):
            if state_type == StateType.CREATE:
                os.mkdir(dst_path)
            elif state_type == StateType.ERROR:
                raise BaseException(
                    FOLDER_EXIST_FORMAT.format(dst_path),
                    "指定目标路径不存在，请检查路径信息",
                )
        ftp_list = FtpCore.get_nlst(ftp_instance)
        local_exist_list = get_exist_files(dst_path)
        work_dir = FtpCore.get_working_dir(ftp_instance)
        download_ftp_path = []

        if file_type == FileType.FILE:
            download_file_list = get_file_list(download_file_name)
            for file in download_file_list:
                file_name = file
                if file not in ftp_list:
                    raise BaseException(
                        FILE_EXIST_FORMAT.format(file),
                        "当前目录中不存在指定下载文件：{}，请检查下载名称".format(file),
                    )
                if file in local_exist_list:
                    if exist_type == FileExistenceType.CANCEL:
                        download_ftp_path.append(os.path.join(dst_path, file))
                        continue
                    elif exist_type == FileExistenceType.OVERWRITE:
                        os.remove(os.path.join(dst_path, file))
                    elif exist_type == FileExistenceType.RENAME:
                        file_name = generate_local_name(local_exist_list, file)
                    else:
                        raise NotImplementedError()
                try:
                    download_file = FtpCore.ftp_download_file(
                        ftp_instance,
                        os.path.join(work_dir, file),
                        os.path.join(dst_path, file_name),
                    )
                except Exception as e:
                    raise BaseException(FTP_DOWNLOAD_FORMAT.format(file), "文件下载失败，请检查FTP连接")

                download_ftp_path.append(download_file)

        elif file_type == FileType.FOLDER:
            download_folder_list = get_file_list(download_folder_name)
            for folder in download_folder_list:
                if folder not in ftp_list:
                    raise BaseException(
                        FOLDER_EXIST_FORMAT.format(folder),
                        "当前目录中不存在指定下载文件夹：{}，请检查下载名称".format(folder),
                    )
                folder_new = folder
                if folder in local_exist_list:
                    if exist_type == FileExistenceType.CANCEL:
                        download_ftp_path.append(os.path.join(dst_path, folder))
                        continue
                    elif exist_type == FileExistenceType.OVERWRITE:
                        os.rmdir(os.path.join(dst_path, folder))
                    elif exist_type == FileExistenceType.RENAME:
                        folder_new = generate_local_name(local_exist_list, folder)
                    else:
                        raise NotImplementedError()

                try:
                    download_folder = FtpCore.ftp_download_dir(
                        ftp_instance,
                        os.path.join(work_dir, folder),
                        os.path.join(dst_path, folder_new),
                    )
                except Exception as e:
                    raise BaseException(
                        FTP_DOWNLOAD_FORMAT.format(folder),
                        "文件下载失败，请检查FTP连接",
                    )

                download_ftp_path.append(download_folder)

        else:
            raise NotImplementedError()

        return download_ftp_path

    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("file_type", required=False),
            atomicMg.param(
                "delete_file_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_file_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FILE.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "delete_folder_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.delete_folder_name.show",
                        expression="return $this.file_type.value == '{}'".format(FileType.FOLDER.value),
                    )
                ],
                required=True,
            ),
        ],
        outputList=[
            atomicMg.param("delete_ftp_result", types="Bool"),
        ],
    )
    def ftp_delete(
        ftp_instance: ftplib.FTP,
        file_type: FileType = FileType.FILE,
        delete_file_name: str = "",
        delete_folder_name: str = "",
    ):
        exist_list = FtpCore.get_nlst(ftp_instance)
        try:
            if file_type == FileType.FILE:
                delete_file_list = get_file_list(delete_file_name)
                for item in delete_file_list:
                    if item not in exist_list:
                        raise BaseException(
                            FTP_DELETE_FORMAT.format(delete_file_name),
                            "当前工作目录中文件不存在，请检查文件名",
                        )
                    FtpCore.ftp_delete_file(ftp_instance, item)
                return True
            elif file_type == FileType.FOLDER:
                delete_folder_list = get_file_list(delete_folder_name)
                for item in delete_folder_list:
                    if item not in exist_list:
                        raise BaseException(
                            FTP_DELETE_FORMAT.format(delete_folder_name),
                            "当前工作目录中文件夹不存在，请检查待删除名称",
                        )
                    FtpCore.ftp_delete_dir(ftp_instance, item)
                return True
            else:
                raise NotImplementedError()
        except Exception as e:
            raise BaseException(FTP_DELETE_FORMAT.format(e), "请检查文件/文件夹是否已删除")
