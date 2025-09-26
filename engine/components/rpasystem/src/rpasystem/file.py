import re
import time

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg

from rpasystem import *
from rpasystem.error import *
from rpasystem.utils import *


class File:
    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                required=True,
            ),
            atomicMg.param("exist_type", required=False),
        ],
    )
    def file_exist(file_path: str = "", exist_type: ExistType = ExistType.EXIST) -> bool:
        """
        判断文件是否存在
        """

        if exist_type == ExistType.EXIST:
            return os.path.isfile(file_path)
        elif exist_type == ExistType.NOT_EXIST:
            return not os.path.isfile(file_path)
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "dst_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                required=True,
            ),
            atomicMg.param(
                "file_name",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
                required=True,
            ),
            atomicMg.param(
                "exist_options",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param(
                "new_file_path",
                types="Str",
                formType=AtomicFormTypeMeta(type=AtomicFormType.RESULT.value),
            ),
        ],
    )
    def file_create(
        dst_path: str = "",
        file_name: str = "",
        exist_options: OptionType = OptionType.GENERATE,
    ) -> str:
        """
        新建文件，指定目标路径和文件名称，返回创建的文件路径
        """
        if not folder_is_exists(dst_path):
            raise BaseException(
                FOLDER_PATH_ERROR_FORMAT.format(dst_path),
                "填写的目录路径不存在，请检查目标路径！",
            )
        file_path = os.path.join(dst_path, file_name)
        if os.path.isfile(file_path):
            if exist_options == OptionType.OVERWRITE:
                os.remove(file_path)
            elif exist_options == OptionType.SKIP:
                return file_path
            elif exist_options == OptionType.GENERATE:
                file_path = generate_copy(dst_path, file_name)
            else:
                raise NotImplementedError()
        with open(file_path, "w") as file:
            pass
        return file_path

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("delete_options", required=False),
        ],
        outputList=[
            atomicMg.param("delete_file_result", types="Str"),
        ],
    )
    def file_delete(file_path: str = "", delete_options: DeleteType = DeleteType.DELETE):
        """
        删除指定文件
        """
        if not os.path.isfile(file_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(file_path), "文件不存在，请检查文件路径！")
        if delete_options == DeleteType.DELETE:
            try:
                os.remove(file_path)
            except PermissionError as e:
                raise BaseException(
                    PermissionError_FORMAT.format(file_path),
                    "文件被占用，请关闭文件后重试！",
                )
        elif delete_options == DeleteType.TRASH:
            try:
                from send2trash import send2trash

                send2trash(file_path)
            except OSError as e:
                raise BaseException(
                    PermissionError_FORMAT.format(file_path),
                    "文件被占用，请关闭文件后重试！",
                )
        else:
            raise NotImplementedError()
        return True

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "target_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "file_name",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
                required=False,
            ),
            atomicMg.param(
                "copy_options",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("copy_file_path", types="Str"),
        ],
    )
    def file_copy(
        file_path: str = "",
        target_path: str = "",
        state_type: StateType = StateType.ERROR,
        file_name: str = "",
        copy_options: OptionType = OptionType.GENERATE,
    ) -> str:
        """
        复制文件到指定目录
        """
        if not os.path.isfile(file_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(file_path), "文件不存在，请检查文件路径！")
        if not folder_is_exists(target_path):
            if state_type == StateType.ERROR:
                raise BaseException(
                    FOLDER_PATH_ERROR_FORMAT.format(target_path),
                    "指定目录有误，请检查路径信息！",
                )
            elif state_type == StateType.CREATE:
                os.makedirs(target_path, exist_ok=True)
            else:
                raise NotImplementedError()

        base_name = os.path.basename(file_path)

        if not file_name:
            file_name = base_name
        else:
            if "." in base_name:
                prefix = os.path.splitext(file_path)[1]
                file_name = "".join([file_name, prefix])
            else:
                raise BaseException(
                    FILE_TYPE_ERROR_FORMAT.format(base_name),
                    "文件扩展名缺失，请检查文件名称是否正确！",
                )

        file_copy_path = os.path.join(target_path, file_name)

        if os.path.isfile(file_copy_path):
            if copy_options == OptionType.OVERWRITE:
                os.remove(file_copy_path)
            elif copy_options == OptionType.SKIP:
                return file_copy_path
            elif copy_options == OptionType.GENERATE:
                file_copy_path = generate_copy(target_path, file_name)
            else:
                raise NotImplementedError()

        if file_path != file_copy_path:
            import shutil

            shutil.copyfile(file_path, file_copy_path)
        return file_copy_path

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "msg",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON.value,
                    params={"size": "middle"},
                ),
            ),
            atomicMg.param("file_option", required=False),
            atomicMg.param("write_type", required=False),
            atomicMg.param("encode_type", required=False),
        ],
        outputList=[
            atomicMg.param("write_file_path", types="Str"),
        ],
    )
    def file_write(
        file_path: str = "",
        file_option: StateType = StateType.ERROR,
        msg: str = "",
        write_type: WriteType = WriteType.APPEND,
        encode_type: EncodeType = EncodeType.DEFAULT,
    ) -> str:
        """
        指定文件中写入内容
        """
        SUPPORT_FORMAT = [".txt", ".docx", ".md", ".py", ".json", ".csv", ".html"]
        if not os.path.isfile(file_path):
            if file_option == StateType.CREATE:
                with open(file_path, "w") as file:
                    pass
            elif file_option == StateType.ERROR:
                raise BaseException(
                    FILE_PATH_ERROR_FORMAT.format(file_path),
                    "目标文件不存在，请检查文件路径！",
                )
            else:
                raise NotImplementedError()

        file_ext = os.path.splitext(file_path)[1]
        if file_ext not in SUPPORT_FORMAT:
            raise BaseException(
                READ_TYPE_ERROR_FORMAT.format(file_path, SUPPORT_FORMAT),
                "当前文件格式不支持内容读取，请重新选择",
            )

        if encode_type == EncodeType.DEFAULT:
            encoding = get_file_encoding_type(file_path)
        elif encode_type in [
            EncodeType.ANSI,
            EncodeType.UTF8,
            EncodeType.UTF16,
            EncodeType.UTF_16_BE,
            EncodeType.GB2312,
            EncodeType.GBK,
            EncodeType.GB18030,
        ]:
            encoding = encode_type.value
        else:
            raise NotImplementedError()

        if write_type == WriteType.OVERWRITE:
            with open(file_path, "w", encoding=encoding) as file:
                file.write(msg)

        elif write_type == WriteType.APPEND:
            with open(file_path, "a", encoding=encoding) as file:
                file.write(msg)
        else:
            raise NotImplementedError()
        return file_path

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[
            atomicMg.param("file_encoding_type", types="Str"),
        ],
    )
    def get_file_encoding_type(file_path: str = "") -> str:
        """
        获取文件编码类型
        :param file_path: 文件路径
        :return: file_encoding_type: 编码类型
        """
        if not os.path.isfile(file_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(file_path), "文件不存在，请检查路径信息！")
        file_encoding_type = get_file_encoding_type(file_path)
        return file_encoding_type

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "read_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
            atomicMg.param("encode_type", required=False),
        ],
        outputList=[
            atomicMg.param("read_file_content", types="Any"),
        ],
    )
    def file_read(
        file_path: str = "",
        read_type: ReadType = ReadType.ALL,
        encode_type: EncodeType = EncodeType.DEFAULT,
    ):
        """
        读取文件内容
        """
        SUPPORT_FORMAT = [".txt", ".docx", ".md", ".py", ".json", ".csv"]
        if not os.path.isfile(file_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(file_path), "文件不存在，请检查路径信息！")

        file_ext = os.path.splitext(file_path)[1]
        if not file_ext or file_ext not in SUPPORT_FORMAT:
            raise BaseException(
                READ_TYPE_ERROR_FORMAT.format(file_path, SUPPORT_FORMAT),
                "当前文件格式不支持内容读取，请重新选择",
            )
        if encode_type == EncodeType.DEFAULT:
            encoding = get_file_encoding_type(file_path)
        elif encode_type in [
            EncodeType.ANSI,
            EncodeType.UTF8,
            EncodeType.UTF16,
            EncodeType.UTF_16_BE,
            EncodeType.GB2312,
            EncodeType.GBK,
            EncodeType.GB18030,
        ]:
            encoding = encode_type.value
        else:
            raise NotImplementedError()

        try:
            if read_type == ReadType.ALL:
                with open(file_path, encoding=encoding) as f:
                    read_file_content = f.read()
            elif read_type == ReadType.List:
                with open(file_path, encoding=encoding) as f:
                    read_file_content = f.readlines()
                    read_file_content = [line.rstrip("\r\n") for line in read_file_content]
            elif read_type == ReadType.BYTE:
                with open(file_path, "rb") as f:
                    read_file_content = f.read()
            else:
                raise NotImplementedError()
        except UnicodeError as e:
            encode_type_file = get_file_encoding_type(file_path)
            raise BaseException(
                ENCODE_TYPE_ERROR_FORMAT.format(encode_type_file, encode_type),
                "指定的编码类型出现错误，请检查编码类型",
            )

        return read_file_content

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "target_folder",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "file_name",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                required=False,
            ),
            atomicMg.param(
                "exist_options",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("move_file_path", types="Str"),
        ],
    )
    def file_move(
        file_path: str = "",
        target_folder: str = "",
        state_type: StateType = StateType.ERROR,
        file_name: str = "",
        exist_options: OptionType = OptionType.GENERATE,
    ) -> str:
        """
        移动文件到目标文件夹。
        """
        if not os.path.isfile(file_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(file_path), "文件不存在，请检查文件路径")
        if not folder_is_exists(target_folder):
            if state_type == StateType.CREATE:
                os.makedirs(target_folder, exist_ok=True)
            elif state_type == StateType.ERROR:
                raise BaseException(
                    FOLDER_PATH_ERROR_FORMAT.format(target_folder),
                    "文件夹不存在，请检查文件夹路径",
                )
            else:
                raise NotImplementedError()

        pre_file_name = os.path.basename(file_path)

        if not file_name:
            file_name = pre_file_name
        else:
            if "." in pre_file_name:
                prefix = os.path.splitext(file_path)[1]
                file_name = "".join([file_name, prefix])
            else:
                raise BaseException(
                    FILE_TYPE_ERROR_FORMAT.format(pre_file_name),
                    "文件扩展名缺失，请检查文件名称是否正确！",
                )

        target_path = os.path.join(target_folder, file_name)

        if os.path.isfile(target_path):
            if exist_options == OptionType.SKIP:
                return target_path
            elif exist_options == OptionType.GENERATE:
                target_path = generate_copy(target_folder, file_name)
            elif exist_options == OptionType.OVERWRITE:
                pass
            else:
                raise NotImplementedError()

        import shutil

        shutil.move(file_path, target_path)
        return target_path

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "new_name",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                required=True,
            ),
            atomicMg.param(
                "exist_options",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("rename_file_path", types="Str"),
        ],
    )
    def file_rename(
        file_path: str = "",
        new_name: str = "",
        exist_options: OptionType = OptionType.GENERATE,
    ) -> str:
        """
        文件重命名
        :param file_path: 重命名文件路径
        :param new_name: 重命名名称， 不加文件扩展名
        :param exist_options: 文件存在时 覆盖/跳过/创建副本
        :return: 重命名后文件路径
        """
        if not os.path.isfile(file_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(file_path), "文件不存在，请检查文件路径")

        if new_name == get_file_name_only(file_path):
            raise BaseException(
                RENAME_ERROR_FORMAT.format(new_name),
                "重命名名称与原名称一致，请检查输入内容",
            )

        file_ext = os.path.splitext(file_path)[1]
        file_dir = os.path.dirname(file_path)
        new_name = new_name + file_ext
        rename_file_path = os.path.join(file_dir, new_name)

        if os.path.isfile(rename_file_path):
            if exist_options == OptionType.SKIP:
                return file_path
            elif exist_options == OptionType.GENERATE:
                rename_file_path = generate_copy(file_dir, new_name)
            elif exist_options == OptionType.OVERWRITE:
                os.remove(rename_file_path)
            else:
                raise NotImplementedError()

        os.rename(file_path, rename_file_path)
        return rename_file_path

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "folder_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param("find_type", required=True),
            atomicMg.param(
                "search_pattern",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                required=True,
            ),
            atomicMg.param("traverse_subfolder", level=AtomicLevel.ADVANCED.value, required=False),
        ],
        outputList=[
            atomicMg.param("find_file_result", types="List"),
        ],
    )
    def file_search(
        folder_path: str = "",
        find_type: SearchType = SearchType.FUZZY,
        search_pattern: str = "",
        traverse_subfolder: TraverseType = TraverseType.NO,
    ) -> list:
        """
        查找文件
        """
        if not folder_is_exists(folder_path):
            raise BaseException(
                FOLDER_PATH_ERROR_FORMAT.format(folder_path),
                "指定文件夹目录不存在，请检查路径信息！",
            )
        if not search_pattern:
            raise BaseException(
                MSG_EMPTY_FORMAT.format(search_pattern),
                "待查找文件名为空，请检查输入内容",
            )

        find_file_result = []

        for root, dirs, files in os.walk(folder_path, topdown=True):
            for file in files:
                if find_type == SearchType.EXACT and file == search_pattern:
                    find_file_result.append(os.path.join(root, file))
                if (
                    find_type == SearchType.FUZZY
                    and search_pattern in file
                    or find_type == SearchType.REGEX
                    and re.search(search_pattern, file)
                ):
                    find_file_result.append(os.path.join(root, file))

            if traverse_subfolder == TraverseType.YES:
                continue
            elif traverse_subfolder == TraverseType.NO:
                break
            else:
                raise NotImplementedError()

        return find_file_result

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param("status_type", required=False),
            atomicMg.param("wait_time", types="Int", required=False),
        ],
        outputList=[
            atomicMg.param("wait_file_result", types="Str"),
        ],
    )
    def file_wait_status(
        file_path: str = "",
        status_type: StatusType = StatusType.CREATED,
        wait_time: int = 10,
    ) -> bool:
        """
        等待文件被创建/被删除
        """
        start_time = time.time()
        file_status = os.path.isfile(file_path)
        if status_type == StatusType.DELETED and not file_status:
            raise BaseException(
                FILE_PATH_ERROR_FORMAT.format(file_path),
                "文件不存在无法删除，请检查路径信息",
            )

        while time.time() - start_time <= wait_time:
            file_status = os.path.isfile(file_path)
            if (status_type == StatusType.CREATED and file_status) or (
                status_type == StatusType.DELETED and not file_status
            ):
                return True
            time.sleep(1)

        return False

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"file_type": "file"},
                ),
            ),
            atomicMg.param("info_type", required=False),
        ],
        outputList=[
            atomicMg.param("file_info", types="Dict"),
        ],
    )
    def file_info(file_path: str = "", info_type: InfoType = InfoType.ALL) -> dict:
        """
        获取文件信息
        """
        if not os.path.isfile(file_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(file_path), "文件不存在，请检查路径信息")

        abs_path = os.path.abspath(file_path)
        file_info = {
            "abs_path": abs_path,
            "root": os.path.splitdrive(abs_path)[0],
            "directory": os.path.dirname(abs_path),
            "name_ext": os.path.basename(file_path),
            "name": get_file_name_only(abs_path),
            "extension": os.path.splitext(file_path)[1],
            "size": os.path.getsize(abs_path),
            "c_time": convert_time_format(os.path.getctime(abs_path)),
            "m_time": convert_time_format(os.path.getmtime(abs_path)),
        }

        if info_type == InfoType.ALL:
            return file_info
        elif str(info_type.value) in file_info:
            return file_info[info_type.value]
        else:
            raise NotImplementedError()

    @staticmethod
    @atomicMg.atomic(
        "File",
        inputList=[
            atomicMg.param(
                "folder_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "excel_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.excel_path.show",
                        expression="return $this.output_type.value == '{}'".format(OutputType.EXCEL.value),
                    )
                ],
                required=True,
            ),
            atomicMg.param(
                "state_type",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.state_type.show",
                        expression="return $this.output_type.value == '{}'".format(OutputType.EXCEL.value),
                    )
                ],
            ),
            atomicMg.param(
                "excel_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.excel_name.show",
                        expression="return $this.output_type.value == '{}'".format(OutputType.EXCEL.value),
                    )
                ],
            ),
            atomicMg.param("output_type", required=False),
            atomicMg.param("sort_method", level=AtomicLevel.ADVANCED.value, required=False),
            atomicMg.param(
                "sort_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.sort_type.show",
                        expression="return $this.sort_method.value ['{}', '{}']".format(
                            SortMethod.CTIME.value, SortMethod.MTIME.value
                        ),
                    )
                ],
                level=AtomicLevel.ADVANCED.value,
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("file_list", types="List"),
        ],
    )
    def get_file_list(
        folder_path: str = "",
        traverse_subfolder: TraverseType = TraverseType.NO,
        output_type: OutputType = OutputType.LIST,
        excel_path: str = "",
        state_type: StateType = StateType.ERROR,
        excel_name: str = "1.xlsx",
        sort_method: SortMethod = SortMethod.NONE,
        sort_type: SortType = SortType.ASCENDING,
    ) -> list:
        """
        获取文件列表
        """
        if not folder_is_exists(folder_path):
            raise BaseException(
                FOLDER_PATH_ERROR_FORMAT.format(folder_path),
                "文件夹不存在，请检查路径信息",
            )

        # 获取文件列表(去除隐藏文件)
        file_list = []
        if traverse_subfolder == TraverseType.YES:
            for root, _, files in os.walk(folder_path, topdown=True):
                file_list.extend(os.path.join(root, file) for file in files if not file.startswith("."))
        elif traverse_subfolder == TraverseType.NO:
            file_list = [
                os.path.join(folder_path, file)
                for file in os.listdir(folder_path)
                if (os.path.isfile(os.path.join(folder_path, file))) and not file.startswith(".")
            ]
        else:
            raise NotImplementedError()

        # 排序
        if sort_method == SortMethod.NONE:
            pass
        elif sort_method == SortMethod.CTIME:
            file_list = sorted(file_list, key=lambda x: os.path.getctime(x))
            file_list = file_list[::-1] if sort_type == SortType.DESCENDING else file_list
        elif sort_method == SortMethod.MTIME:
            file_list = sorted(file_list, key=lambda x: os.path.getmtime(x))
            file_list = file_list[::-1] if sort_type == SortType.DESCENDING else file_list
        else:
            raise NotImplementedError()

        # 输出
        if output_type == OutputType.EXCEL:
            if not folder_is_exists(excel_path):
                if state_type == StateType.ERROR:
                    raise BaseException(
                        FILE_PATH_ERROR_FORMAT.format(excel_path),
                        "指定excel存储路径不存在，请检查路径信息",
                    )
                elif state_type == StateType.CREATE:
                    os.makedirs(excel_path, exist_ok=True)
                else:
                    raise NotImplementedError()

            if not os.path.splitext(excel_name)[1] == ".xlsx":
                if os.path.splitext(excel_name)[1]:
                    excel_name = get_file_name_only(excel_name)
                excel_name += ".xlsx"

            excel_path = os.path.join(excel_path, excel_name)
            list_to_excel(path_list=file_list, excel_path=excel_path)
            return file_list
        elif output_type == OutputType.LIST:
            return file_list
        else:
            raise NotImplementedError()
