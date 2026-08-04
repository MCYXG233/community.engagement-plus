"""日志配置模块：提供统一的日志格式、轮转和级别管理。"""

import logging
import logging.handlers
import os
from typing import Optional


class PluginLogger:
    """插件日志管理器，支持文件轮转和统一格式。"""

    def __init__(
        self,
        data_dir: str,
        plugin_name: str = "community_engagement",
        max_bytes: int = 5 * 1024 * 1024,  # 5MB
        backup_count: int = 5,
        level: int = logging.INFO,
    ):
        self.data_dir = data_dir
        self.plugin_name = plugin_name
        self.log_dir = os.path.join(data_dir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)

        # 创建主日志器
        self.logger = logging.getLogger(f"plugin.{plugin_name}")
        self.logger.setLevel(level)

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 文件处理器（带轮转）
            log_file = os.path.join(self.log_dir, f"{plugin_name}.log")
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(level)

            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上

            # 统一格式
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self, module_name: Optional[str] = None) -> logging.Logger:
        """获取子模块日志器。"""
        if module_name:
            return logging.getLogger(f"plugin.{self.plugin_name}.{module_name}")
        return self.logger

    def set_level(self, level: int) -> None:
        """动态调整日志级别。"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# 全局日志管理器实例
_log_manager: Optional[PluginLogger] = None


def setup_logging(data_dir: str, plugin_name: str = "community_engagement") -> PluginLogger:
    """初始化日志系统并返回管理器。"""
    global _log_manager
    if _log_manager is None:
        _log_manager = PluginLogger(data_dir, plugin_name)
    return _log_manager


def get_logger(module_name: Optional[str] = None) -> logging.Logger:
    """获取日志器的便捷函数。"""
    if _log_manager is None:
        return logging.getLogger(f"plugin.community_engagement.{module_name or ''}")
    return _log_manager.get_logger(module_name)
