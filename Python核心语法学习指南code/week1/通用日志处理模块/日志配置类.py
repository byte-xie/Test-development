import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import sys

# 导入自定义的setup_logger函数，用于创建高级日志记录器
from Python核心语法学习指南code.week1.通用日志处理模块.高级日志模块实现 import setup_logger


class LoggerFactory:
    """
    日志工厂类，负责统一管理和创建日志记录器（logger）实例。
    支持按名称缓存和复用日志对象，避免重复创建。
    """
    _loggers = {}  # 类变量，保存所有已创建的日志记录器对象，key为logger名称

    @classmethod
    def get_logger(cls, name="app", config=None):
        """
        获取或创建指定名称的日志记录器。
        参数：
            name (str): 日志记录器名称，通常为模块名或业务名。
            config (dict): 可选，日志配置字典，支持覆盖默认配置。
        返回值：
            logger (logging.Logger): 配置好的日志记录器对象。
        说明：
            - 若同名logger已存在，则直接返回。
            - 支持自定义日志文件名、级别、轮转策略等。
        """
        if name in cls._loggers:
            return cls._loggers[name]  # 已存在则直接返回

        # 默认配置
        default_config = {
            "log_file": f"{name}.log",         # 日志文件名，默认与logger名称一致
            "level": "INFO",                  # 日志级别，默认INFO
            "max_bytes": 10 * 1024 * 1024,     # 单文件最大10MB，超出后轮转
            "backup_count": 7,                 # 最多保留7个备份
            "when": "midnight",               # 时间轮转单位，默认每天0点
            "interval": 1                      # 时间轮转间隔，默认1天
        }

        # 合并自定义配置（如有）
        if config:
            default_config.update(config)

        # 解析日志级别字符串为logging模块常量
        level = getattr(logging, default_config["level"].upper())

        # 创建日志记录器，调用自定义setup_logger
        logger = setup_logger(
            name=name,
            log_file=default_config["log_file"],
            level=level,
            max_bytes=default_config["max_bytes"],
            backup_count=default_config["backup_count"],
            when=default_config["when"],
            interval=default_config["interval"]
        )

        cls._loggers[name] = logger  # 缓存logger对象，便于复用
        return logger


# 使用示例
app_logger = LoggerFactory.get_logger("app")  # 获取名为"app"的日志记录器，使用默认配置

db_logger = LoggerFactory.get_logger("database", {
    "log_file": "logs/db.log",  # 指定数据库日志文件路径
    "level": "DEBUG"             # 设置日志级别为DEBUG
})

app_logger.info("应用程序启动")      # 记录一条INFO级别日志

db_logger.debug("数据库连接建立")  # 记录一条DEBUG级别日志
