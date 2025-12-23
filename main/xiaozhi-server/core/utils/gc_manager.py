"""
The global GC management module performs 
garbage collection periodically to avoid GIL (Global Interpreter Lock) 
issues caused by frequent GC triggers.

"""

import gc
import asyncio
import threading
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class GlobalGCManager:
    """全局垃圾回收管理器"""

    def __init__(self, interval_seconds=300):
        """
        初始化GC管理器

        Args:
            interval_seconds: GC执行间隔（秒），默认300秒（5分钟）
        """
        self.interval_seconds = interval_seconds
        self._task = None
        self._stop_event = asyncio.Event()
        self._lock = threading.Lock()

    async def start(self):
        """启动定时GC任务"""
        if self._task is not None:
            logger.bind(tag=TAG).warning("The GC manager is already running.")
            return

        logger.bind(tag=TAG).info(f"Start the global GC manager，Interval {self.interval_seconds} seconds")
        self._stop_event.clear()
        self._task = asyncio.create_task(self._gc_loop())

    async def stop(self):
        """停止定时GC任务"""
        if self._task is None:
            return

        logger.bind(tag=TAG).info("Stop the global GC manager")
        self._stop_event.set()

        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self._task = None

    async def _gc_loop(self):
        """GC循环任务"""
        try:
            while not self._stop_event.is_set():
                # 等待指定间隔
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=self.interval_seconds
                    )
                    # 如果stop_event被设置，退出循环
                    break
                except asyncio.TimeoutError:
                    # 超时表示到了执行GC的时间
                    pass

                # 执行GC
                await self._run_gc()

        except asyncio.CancelledError:
            logger.bind(tag=TAG).info("GC loop task was canceled")
            raise
        except Exception as e:
            logger.bind(tag=TAG).error(f"GC loop task exception: {e}")
        finally:
            logger.bind(tag=TAG).info("The GC loop task has exited.")

    async def _run_gc(self):
        """执行垃圾回收"""
        try:
            # Perform garbage collection (GC) in a thread pool to avoid blocking the event loop.
            loop = asyncio.get_running_loop()

            def do_gc():
                with self._lock:
                    before = len(gc.get_objects())
                    collected = gc.collect()
                    after = len(gc.get_objects())
                    return before, collected, after

            before, collected, after = await loop.run_in_executor(None, do_gc)
            logger.bind(tag=TAG).debug(
                f"Global GC complete - objects reclaimed: {collected}, "
                f"Object count: {before} -> {after}"
            )
        except Exception as e:
            logger.bind(tag=TAG).error(f"Error executing GC: {e}")


# 全局单例
_gc_manager_instance = None


def get_gc_manager(interval_seconds=300):
    """
    获取全局GC管理器实例（单例模式）

    Args:
        interval_seconds: GC执行间隔（秒），默认300秒（5分钟）

    Returns:
        GlobalGCManager实例
    """
    global _gc_manager_instance
    if _gc_manager_instance is None:
        _gc_manager_instance = GlobalGCManager(interval_seconds)
    return _gc_manager_instance
