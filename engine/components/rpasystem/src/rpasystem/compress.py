import os

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg

from rpasystem import *
from rpasystem.core.compress_core import CompressCore
from rpasystem.error import *
from rpasystem.utils import folder_is_exists, get_file_name_only

CompressCore = CompressCore()


class Compress:
    """压缩解压"""

    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param("file_type", required=True),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "files"},
                ),
                required=True,
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.file_type.value != '{}'".format(FileFolderType.FOLDER.value),
                    )
                ],
            ),
            atomicMg.param(
                "folder_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                required=True,
                dynamics=[
                    DynamicsItem(
                        key="$this.folder_path.show",
                        expression="return $this.file_type.value != '{}'".format(FileFolderType.FILE.value),
                    )
                ],
            ),
            atomicMg.param(
                "compress_name",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON.value),
                required=False,
            ),
            atomicMg.param(
                "compress_dir",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                required=True,
            ),
            atomicMg.param("pwd", required=False),
            atomicMg.param("save_type", level=AtomicLevel.ADVANCED.value, required=False),
        ],
        outputList=[
            atomicMg.param("compress_path", types="Str"),
        ],
    )
    def compress(
        file_type: FileFolderType = FileFolderType.FILE,
        file_path: str = "",
        folder_path: str = "",
        compress_dir: str = "",
        state_type: StateType = StateType.ERROR,
        compress_name: str = "",
        pwd: str = "",
        save_type: SaveType = SaveType.SAVE,
    ):
        if file_type == FileFolderType.FILE and not file_path:
            raise ValueError("待压缩文件路径不能为空，请检查所选内容")
        if file_type == FileFolderType.FOLDER and not folder_path:
            raise ValueError("待压缩文件夹路径不能为空，请检查所选内容")
        if file_type == FileFolderType.BOTH and not (file_path or folder_path):
            raise ValueError("待压缩文件和文件夹路径不能为空，请检查所选内容")

        items_file = [path.strip() for path in file_path.split(",")]
        items_folder = [path.strip() for path in folder_path.split(",")]
        items = items_folder + items_file
        if not compress_name:
            if not folder_path:
                compress_name = get_file_name_only(items[1])
            else:
                compress_name = get_file_name_only(items[0])
        if not folder_is_exists(compress_dir):
            if state_type == StateType.ERROR:
                raise BaseException(
                    FOLDER_PATH_ERROR_FORMAT.format(compress_dir),
                    "指定目标路径不存在，请检查路径信息",
                )
            elif state_type == StateType.CREATE:
                os.makedirs(compress_dir, exist_ok=True)
            else:
                raise NotImplementedError()

        compress_path = CompressCore.compress(items=items, file_name=compress_name, dest_path=compress_dir, pwd=pwd)
        if save_type == SaveType.SAVE:
            pass
        elif save_type == SaveType.DELETE:
            for item in items:
                if item:
                    from send2trash import send2trash

                    send2trash(item)
        else:
            raise NotImplementedError()
        return compress_path

    @staticmethod
    @atomicMg.atomic(
        "System",
        inputList=[
            atomicMg.param(
                "source_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                required=True,
            ),
            atomicMg.param(
                "target_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                required=True,
            ),
            atomicMg.param("pwd", required=False),
            atomicMg.param("save_type", level=AtomicLevel.ADVANCED.value, required=False),
        ],
        outputList=[
            atomicMg.param("uncompress_path", types="Str"),
        ],
    )
    def uncompress(
        source_path: str = "",
        target_path: str = "",
        status_type: StateType = StateType.ERROR,
        pwd: str = "",
        save_type: SaveType = SaveType.SAVE,
    ):
        if not os.path.isfile(source_path):
            raise BaseException(FILE_PATH_ERROR_FORMAT.format(source_path), "文件不存在，请检查文件路径")
        if not folder_is_exists(target_path):
            if status_type == StateType.CREATE:
                os.makedirs(target_path, exist_ok=True)
            elif status_type == StateType.ERROR:
                raise BaseException(
                    FOLDER_PATH_ERROR_FORMAT.format(target_path),
                    "指定目录不存在，请检查路径信息",
                )

        uncompress_path = CompressCore.uncompress(source_path=source_path, dest_path=target_path, pwd=pwd)
        if save_type == SaveType.SAVE:
            pass
        elif save_type == SaveType.DELETE:
            os.remove(source_path)
        else:
            raise NotImplementedError()
        return uncompress_path
