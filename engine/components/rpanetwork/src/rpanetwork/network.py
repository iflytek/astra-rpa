import os.path

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpanetwork import FileExistenceType, RequestType, SaveType, StateType
from rpanetwork.core_network import NetworkCore
from rpanetwork.error import *
from rpanetwork.utils import (
    file_is_exist,
    folder_is_exist,
    generate_local_name,
    get_exist_files,
)


class Network:
    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("url", types="Str", required=True),
            atomicMg.param("request_type"),
            atomicMg.param("headers", types="Str", required=False),
            atomicMg.param(
                "body",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.body.show",
                        expression="return [{}, {}].includes($this.request_type.value)".format(
                            repr(RequestType.POST.value), repr(RequestType.PUT.value)
                        ),
                    )
                ],
                required=False,
            ),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.request_type.value == '{}'".format(RequestType.POST.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param("time_out", types="Int", required=False),
            atomicMg.param("save_type", required=False, level=AtomicLevel.ADVANCED.value),
            atomicMg.param(
                "save_path",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
                level=AtomicLevel.ADVANCED.value,
                dynamics=[
                    DynamicsItem(
                        key="$this.save_path.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.YES.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_name.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.YES.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("http_response", types="Any"),
        ],
    )
    def http_request(
        url: str = "",
        request_type: RequestType = RequestType.POST,
        headers=None,
        body=None,
        file_path: str = "",
        time_out: int = 60,
        save_type: SaveType = SaveType.NO,
        save_path: str = "",
        save_name: str = "",
    ):
        if time_out == "" or time_out is None:
            time_out = 60

        if request_type == RequestType.POST:
            if file_path:
                if not file_is_exist(file_path):
                    raise BaseException(
                        FILE_EXIST_FORMAT.format(file_path),
                        "指定文件不存在，请检查文件路径",
                    )
            http_response = NetworkCore.post_request(
                url=url, header=headers, body=body, files=file_path, timeout=time_out
            )
        elif request_type == RequestType.GET:
            http_response = NetworkCore.get_request(url=url, header=headers, timeout=time_out)
        elif request_type == RequestType.CONNECT:
            http_response = NetworkCore.connect_request(url=url, header=headers, timeout=time_out)
        elif request_type == RequestType.HEAD:
            http_response = NetworkCore.head_request(url=url, header=headers, timeout=time_out)
        elif request_type == RequestType.PUT:
            http_response = NetworkCore.put_request(url=url, header=headers, body=body, timeout=time_out)
        elif request_type == RequestType.DELETE:
            http_response = NetworkCore.delete_request(url=url, header=headers, timeout=time_out)
        elif request_type == RequestType.OPTIONS:
            http_response = NetworkCore.options_request(url=url, header=headers, timeout=time_out)
        elif request_type == RequestType.TRACE:
            http_response = NetworkCore.trace_request(url=url, header=headers, timeout=time_out)
        elif request_type == RequestType.PATCH:
            http_response = NetworkCore.patch_request(url=url, header=headers, body=body, timeout=time_out)
        else:
            raise NotImplementedError()

        if save_type == SaveType.YES:
            if not folder_is_exist(save_path):
                raise BaseException(
                    FOLDER_EXIST_FORMAT.format(save_path),
                    "文件夹不存在，请检查路径信息",
                )
            save_path = os.path.join(save_path, save_name)
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(http_response)
                return save_path
            except Exception as e:
                raise ValueError("文件写入失败，请检查文件类型是否正确")
        else:
            return http_response

    @staticmethod
    @atomicMg.atomic(
        "Network",
        inputList=[
            atomicMg.param("url", types="Str"),
            atomicMg.param(
                "dst_dir",
                formType=AtomicFormTypeMeta(
                    AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "rename",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.rename.show",
                        expression="return $this.state_type.value == '{}'".format(StateType.CREATE.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param("state_type", required=False),
            atomicMg.param(
                "exist_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
                required=False,
            ),
        ],
        outputList=[
            atomicMg.param("http_download_path", types="Str"),
        ],
    )
    def http_download(
        url: str = "",
        dst_dir: str = "",
        rename: str = "",
        state_type: StateType = StateType.CREATE,
        exist_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        if not folder_is_exist(dst_dir):
            if state_type == StateType.CREATE:
                os.makedirs(dst_dir, exist_ok=True)
            elif state_type == StateType.ERROR:
                raise BaseException(
                    FOLDER_EXIST_FORMAT.format(dst_dir=dst_dir),
                    "指定目录不存在，请检查路径信息",
                )

        if not rename:
            file_name = url.split("/")[-1]
        else:
            file_name = rename

        if file_name in get_exist_files(dst_dir):
            if exist_type == FileExistenceType.RENAME:
                file_name = generate_local_name(get_exist_files(dst_dir), file_name)
            elif exist_type == FileExistenceType.CANCEL:
                return os.path.join(dst_dir, file_name)
            elif exist_type == FileExistenceType.OVERWRITE:
                os.remove(os.path.join(dst_dir, file_name))
            else:
                raise NotImplementedError()

        download_path = os.path.join(dst_dir, file_name)

        try:
            http_download_path = NetworkCore.http_download(url=url, dst_path=download_path)
            return http_download_path
        except BaseException as e:
            raise BaseException(HTTP_DOWNLOAD_FORMAT.format(e), "文件下载失败")
