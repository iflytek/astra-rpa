import asyncio

from keyboard import add_hotkey, remove_hotkey

from ..core.logger import logger


class HotKeyTask:
    def __init__(self, shortcuts: list = None, **kwargs):
        """
        构建热键监听的类

        shortcuts: `List`, 快捷键组合

        Kwargs: 该参数用于构建任务的详细参数状态
        """
        self.shortcuts = shortcuts
        self._h_handle = None  # 用于控制监听事件的对象

    async def callback(self, q: asyncio.Queue, run_event: asyncio.Event):
        async def handle_hotkey():
            logger.debug("handle_hotkey: enqueue True to asyncio.Queue")
            await q.put(True)
            try:
                logger.debug(f"handle_hotkey: queue size after put -> {q.qsize()}")
            except Exception:
                pass

        def on_hotkey_press(loop):
            """loop主要作用于当前事件循环，在同一时间循环下进行任务执行"""
            try:
                is_set = run_event.is_set()
            except Exception as e:
                logger.exception(f"on_hotkey_press: failed to read run_event.is_set(): {e}")
                is_set = False
            logger.debug(f"on_hotkey_press: hotkey '{hotkey_expression}' pressed, run_event.is_set={is_set}")
            if is_set:
                logger.info("on_hotkey_press: run_event is set; ignore hotkey")
                return
            loop.call_soon_threadsafe(asyncio.create_task, handle_hotkey())
            logger.debug("on_hotkey_press: scheduled handle_hotkey on event loop")

        loop = asyncio.get_running_loop()
        hotkey_expression = "+".join(self.shortcuts)
        logger.info(f"Registering hotkey '{hotkey_expression}' via keyboard.add_hotkey")
        self._h_handle = add_hotkey(hotkey_expression, on_hotkey_press, args=(loop,))

    def force_end_callback(self):
        """该方法进行热键任务回收"""
        logger.info("force_end_callback: removing hotkey listener")
        remove_hotkey(self._h_handle)
