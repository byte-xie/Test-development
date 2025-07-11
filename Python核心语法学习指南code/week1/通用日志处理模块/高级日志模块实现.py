import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import sys


def setup_logger(name="app",
                 log_file="app.log",
                 level=logging.INFO,
                 max_bytes=10 * 1024 * 1024,  # 10MB
                 backup_count=5,
                 when="midnight",
                 interval=1,
                 formatter=None):
    """
    配置并返回一个高级日志记录器。
    参数：
        name (str): 日志记录器名称，通常为模块名或应用名。
        log_file (str): 日志文件路径。
        level (int): 日志级别，如logging.INFO、logging.DEBUG等。
        max_bytes (int): 单个日志文件的最大字节数，超过后轮转（适用于大小轮转）。
        backup_count (int): 保留的备份日志文件数量。
        when (str): 时间轮转的单位（如'midnight'、'D'、'H'等，适用于时间轮转）。
        interval (int): 时间轮转的间隔数。
        formatter (logging.Formatter): 日志格式化器对象，若为None则使用默认格式。
    返回值：
        logger (logging.Logger): 配置好的日志记录器对象。
    说明：
        支持文件大小轮转、时间轮转、控制台输出等多种日志处理方式。
    """
    # 创建日志文件目录（如果需要）
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)  # 自动创建日志目录，避免因目录不存在导致报错

    # 创建日志记录器对象（同名只会创建一个实例）
    logger = logging.getLogger(name)
    logger.setLevel(level)  # 设置日志级别

    # 防止日志重复记录（清空已存在的处理器）
    if logger.hasHandlers():
        logger.handlers.clear()

    # 设置日志格式化器
    if formatter is None:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )  # 默认格式：时间-名称-级别-文件:行号-消息

    # 文件处理器1：按文件大小轮转
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)  # 设置格式
    logger.addHandler(file_handler)  # 添加到日志记录器

    # 文件处理器2：按时间轮转（如每天0点新建日志文件）
    time_handler = TimedRotatingFileHandler(
        log_file + ".timed",  # 时间轮转日志文件名
        when=when,             # 轮转单位
        interval=interval,     # 轮转间隔
        backupCount=backup_count  # 备份数量
    )
    time_handler.setFormatter(formatter)
    logger.addHandler(time_handler)

    # 控制台处理器：输出到标准输出（如终端/控制台）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 错误邮件处理器（示例，未启用）
    # if enable_email:
    #     mail_handler = SMTPHandler(...)
    #     mail_handler.setLevel(logging.ERROR)
    #     logger.addHandler(mail_handler)

    return logger  # 返回配置好的日志记录器


if __name__ == '__main__':
    # 主程序入口，演示日志模块的用法
    logger = setup_logger()  # 获取一个默认配置的日志记录器

    # 输出不同级别的日志
    logger.debug("调试信息")      # DEBUG级别，调试时使用
    logger.info("普通信息")      # INFO级别，普通运行信息
    logger.warning("警告信息")   # WARNING级别，警告但不影响程序运行
    logger.error("错误信息")     # ERROR级别，程序出错但未崩溃

    # 异常捕获与日志记录
    try:
        1 / 0  # 故意制造一个除零异常
    except Exception as e:
        logger.exception("发生异常: %s", e)  # 记录异常堆栈信息
