import asyncio
import fnmatch
import os
import time
from pathlib import Path
from typing import List, Union

from watchfiles import Change, awatch

from ..core.logger import logger

create_flag = "create"
delete_flag = "delete"
modified_flag = "update"
rename_flag = "rename"


class FileTask:
    def __init__(
        self,
        directory: str = ".",
        relative_sub_path: bool = False,
        events: List[str] = None,
        files_or_type: Union[List[str], None] = None,
        **kwargs,
    ):
        """
        构建文件检查的类

        directory: `str`, 目标文件夹
        relative_sub_path: `bool`, 是否包含子路径
        events: `List[str]`, 监控事件类型, 元素仅支持['create'、'delete'、'update'、'rename']
        files_or_type: `Union[List[str], None]`, 监听单个文件通或配符

        Kwargs: 该参数用于构建任务的详细参数状态

        """
        self.directory = directory
        self.relative_sub_path = relative_sub_path
        self.events = events
        self.files_or_type = files_or_type if files_or_type else []

    def _match_file(self, filepath: str) -> bool:
        filename = os.path.basename(filepath)
        for pattern in self.files_or_type:
            if filename == pattern or fnmatch.fnmatch(filename, pattern):
                return True
        return False

    async def callback(self, q: asyncio.Queue, run_event: asyncio.Event):
        """
        检查回调
        """
        async for changes in awatch(
            self.directory, recursive=self.relative_sub_path, debounce=500
        ):  # debounce判断500ms里是否能一次性监听响应
            if run_event.is_set():
                continue

            deleted_paths = set()
            added_paths = set()
            modified_paths = set()
            final_modified = set()
            renamed_pairs = []
            current_time = time.time()

            for change_type, path in changes:
                logger.info(f"【AsyncFileTask callback】监听文件变化：{change_type} {path}")
                path_obj = Path(path)
                if path_obj.is_dir():  # 忽略目录自身的事件（如父目录MODIFIED）
                    continue

                if change_type == Change.deleted:  # 属于delete事件，则在对应的集合添加
                    deleted_paths.add(path)
                elif change_type == Change.added:  # 属于added事件，则在对应的集合添加
                    added_paths.add(path)
                elif change_type == Change.modified:  #  属于modified事件，则在对应的集合添加
                    if path_obj.exists():  # 验证路径有效性（避免已删除文件残留事件）
                        modified_paths.add((path, current_time))

            # 匹配重命名事件（同一批次DELETED+ADDED配对）
            for deleted_path in list(deleted_paths):
                for added_path in list(added_paths):
                    if (
                        Path(deleted_path).parent == Path(added_path).parent
                        and Path(deleted_path).name != Path(added_path).name
                    ):
                        renamed_pairs.append((deleted_path, added_path))
                        deleted_paths.remove(deleted_path)
                        added_paths.remove(added_path)
                        break

            # 处理剩余事件（过滤高频MODIFIED）
            for path, timestamp in modified_paths:
                if current_time - timestamp < 0.5:
                    final_modified.add(path)

            # 真实的勾选监控事件判断
            if (
                (create_flag in self.events and added_paths)
                or (delete_flag in self.events and deleted_paths)
                or (rename_flag in self.events and renamed_pairs)
                or (modified_flag in self.events and final_modified)
            ):
                await q.put(True)
                continue
