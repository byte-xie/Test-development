# =============================================================================
# 增强版系统监控工具 - 实时监控系统资源使用情况
#
# 功能特性：
# - 多线程并发监控（CPU、内存、网络、磁盘）
# - 智能警报系统（支持冷却时间和声音提醒）
# - 数据历史记录（使用deque限制内存使用）
# - 自动数据导出（CSV格式）
# - 跨平台声音警报支持
# - 详细的系统信息收集
# - 监控摘要和统计信息
# - 配置文件驱动的参数管理
#
# 作者：谢浩亮
# 版本：3.0 (增强版)
# 日期：2024年
# =============================================================================

# 导入必要的库
import psutil  # 用于获取系统和进程信息
import time  # 用于时间相关操作
import logging  # 用于日志记录
import os  # 用于文件和目录操作
import json  # 用于配置文件处理
import threading  # 用于多线程支持
import csv  # 用于数据导出
from datetime import datetime, timedelta  # 用于时间戳和日期计算
from typing import Optional, Dict, Any, List, Tuple  # 类型提示
from collections import deque  # 用于高效的数据历史记录
import platform  # 用于获取平台信息
import subprocess  # 用于执行系统命令
import signal  # 用于信号处理


class EnhancedSystemMonitor:
    """
    增强版系统监控器 - 包含更多高级功能

    这个类提供了比基础版本更强大的系统监控功能，包括：
    - 多线程并发监控：同时监控多个系统指标
    - 智能警报系统：支持冷却时间的警报机制
    - 数据历史记录：使用deque保存最近1000个数据点
    - 自动数据导出：定期导出监控数据到CSV文件
    - 跨平台声音警报：支持Windows、Linux、macOS
    - 监控摘要：提供详细的统计信息

    使用示例：
        monitor = EnhancedSystemMonitor()
        monitor.start_comprehensive_monitoring()  # 开始综合监控
        monitor.stop_monitoring()                # 停止监控
        summary = monitor.get_monitoring_summary()  # 获取监控摘要
    """

    def __init__(self, config_file: str = 'monitor_config.json'):
        """
        初始化增强版系统监控器

        Args:
            config_file (str): 配置文件路径，默认为'monitor_config.json'

        初始化过程：
        1. 加载配置文件
        2. 设置日志系统
        3. 初始化监控状态和数据存储
        4. 准备多线程监控环境
        """
        # 存储配置文件路径
        self.config_file = config_file

        # 加载配置文件，获取监控参数
        self.config = self._load_config()

        # 设置日志系统
        self.logger = self._setup_logging()

        # 监控状态标志（False表示未开始监控）
        self.monitoring = False

        # 监控线程列表（用于多线程监控）
        self.monitor_threads = []

        # 数据历史记录（使用deque限制内存使用，最多保存1000个数据点）
        self.data_history = {
            'cpu': deque(maxlen=1000),  # CPU监控数据历史
            'memory': deque(maxlen=1000),  # 内存监控数据历史
            'network': deque(maxlen=1000),  # 网络监控数据历史
            'disk': deque(maxlen=1000)  # 磁盘监控数据历史
        }

        # 警报历史记录（用于实现警报冷却机制）
        self.alert_history = {}

        # 监控开始时间（用于计算运行时长）
        self.start_time = None

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        从JSON配置文件中加载监控参数，如果配置文件不存在或加载失败，
        则使用默认配置。增强版支持更多的配置选项，包括数据导出、
        警报设置和显示设置。

        Returns:
            Dict[str, Any]: 包含所有监控参数的配置字典

        配置参数说明：
        - cpu_warning_threshold: CPU使用率警告阈值（百分比）
        - memory_warning_threshold: 内存使用率警告阈值（百分比）
        - disk_warning_threshold: 磁盘使用率警告阈值（百分比）
        - network_speed_warning: 网络速度警告阈值（字节/秒）
        - process_cpu_warning: 进程CPU使用率警告阈值（百分比）
        - process_memory_warning: 进程内存使用率警告阈值（百分比）
        - monitor_interval: 监控间隔时间（秒）
        - log_level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        - enable_console_output: 是否启用控制台输出
        - enable_file_output: 是否启用文件输出

        增强功能配置：
        - data_export: 数据导出设置
        - alert_settings: 警报设置（包括声音警报和冷却时间）
        - display_settings: 显示设置（控制输出格式）
        """
        # 默认配置参数（当配置文件不存在时使用）
        default_config = {
            # 基础监控阈值
            "cpu_warning_threshold": 80,  # CPU使用率超过80%时发出警告
            "memory_warning_threshold": 80,  # 内存使用率超过80%时发出警告
            "disk_warning_threshold": 90,  # 磁盘使用率超过90%时发出警告
            "network_speed_warning": 100 * 1024 * 1024,  # 网络速度超过100MB/s时发出警告
            "process_cpu_warning": 50,  # 进程CPU使用率超过50%时发出警告
            "process_memory_warning": 10,  # 进程内存使用率超过10%时发出警告
            "monitor_interval": 1,  # 监控间隔为1秒
            "log_level": "INFO",  # 日志级别为INFO
            "enable_console_output": True,  # 启用控制台输出
            "enable_file_output": True,  # 启用文件输出

            # 数据导出设置
            "data_export": {
                "enable_csv_export": True,  # 启用CSV数据导出
                "export_interval": 60,  # 导出间隔（秒）
                "csv_directory": "exports"  # 导出目录
            },

            # 警报设置
            "alert_settings": {
                "enable_sound_alerts": True,  # 启用声音警报
                "alert_cooldown_seconds": 300  # 警报冷却时间（秒）
            },

            # 显示设置
            "display_settings": {
                "show_per_core_cpu": True,  # 显示每个核心的CPU使用率
                "show_network_interfaces": True,  # 显示网络接口信息
                "show_process_details": False,  # 显示进程详细信息
                "refresh_rate": 1  # 刷新率（秒）
            }
        }

        # 尝试加载配置文件
        try:
            if os.path.exists(self.config_file):
                # 以UTF-8编码打开配置文件
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    # 解析JSON配置
                    config = json.load(f)
                    # 用配置文件中的值更新默认配置
                    default_config.update(config)
                    print(f"成功加载配置文件: {self.config_file}")
        except Exception as e:
            # 如果配置文件加载失败，使用默认配置并记录错误
            print(f"加载配置文件失败，使用默认配置: {e}")

        return default_config

    def _setup_logging(self) -> logging.Logger:
        """
        配置日志系统

        设置统一的日志记录系统，支持同时输出到文件和控制台。
        增强版的日志文件名包含"enhanced"标识，便于区分不同版本。

        Returns:
            logging.Logger: 配置好的日志记录器

        日志配置说明：
        - 日志格式：时间 - 级别 - 消息
        - 时间格式：YYYY-MM-DD HH:MM:SS
        - 文件输出：logs/enhanced_monitor_YYYYMMDD.log
        - 控制台输出：实时显示日志信息
        - 编码：UTF-8（支持中文）
        - 日志级别：从配置文件中读取
        """
        # 创建日志目录（如果不存在）
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"创建日志目录: {log_dir}")

        # 定义日志格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'  # 时间 - 级别 - 消息
        date_format = '%Y-%m-%d %H:%M:%S'  # 时间格式：年-月-日 时:分:秒

        # 创建日志记录器实例
        logger = logging.getLogger('EnhancedSystemMonitor')
        # 设置日志级别（从配置中读取）
        logger.setLevel(getattr(logging, self.config['log_level']))

        # 清除现有的处理器（避免重复添加）
        logger.handlers.clear()

        # 添加文件处理器（如果启用文件输出）
        if self.config['enable_file_output']:
            # 生成日志文件名，包含当前日期和"enhanced"标识
            log_filename = f'{log_dir}/enhanced_monitor_{datetime.now().strftime("%Y%m%d")}.log'
            # 创建文件处理器，使用UTF-8编码
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            # 设置日志格式
            file_handler.setFormatter(logging.Formatter(log_format, date_format))
            # 添加到日志记录器
            logger.addHandler(file_handler)
            print(f"增强版日志文件输出已启用: {log_filename}")

        # 添加控制台处理器（如果启用控制台输出）
        if self.config['enable_console_output']:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            # 设置日志格式
            console_handler.setFormatter(logging.Formatter(log_format, date_format))
            # 添加到日志记录器
            logger.addHandler(console_handler)
            print("增强版控制台日志输出已启用")

        return logger

    def format_bytes(self, bytes_value: int) -> str:
        """
        格式化字节数为可读格式

        将字节数转换为人类可读的格式，自动选择合适的单位。
        支持的单位：B, KB, MB, GB, TB, PB

        Args:
            bytes_value (int): 要格式化的字节数

        Returns:
            str: 格式化后的字符串，如 "1.50 MB"

        示例：
            format_bytes(1024) -> "1.00 KB"
            format_bytes(1048576) -> "1.00 MB"
            format_bytes(1073741824) -> "1.00 GB"
        """
        # 定义字节单位（从小到大）
        units = ['B', 'KB', 'MB', 'GB', 'TB']

        # 遍历所有单位，找到合适的单位
        for unit in units:
            # 如果字节数小于1024，使用当前单位
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            # 否则除以1024，继续检查下一个单位
            bytes_value /= 1024.0

        # 如果所有单位都不合适，使用PB（拍字节）
        return f"{bytes_value:.2f} PB"

    def format_speed(self, bytes_per_sec: float) -> str:
        """
        格式化网络速度

        将网络速度（字节/秒）转换为人类可读的格式，自动选择合适的单位。
        支持的单位：B/s, KB/s, MB/s, GB/s

        Args:
            bytes_per_sec (float): 网络速度（字节/秒）

        Returns:
            str: 格式化后的字符串，如 "1.50 MB/s"

        示例：
            format_speed(1024) -> "1.00 KB/s"
            format_speed(1048576) -> "1.00 MB/s"
            format_speed(1073741824) -> "1.00 GB/s"
        """
        # 根据速度大小选择合适的单位
        if bytes_per_sec >= 1024 ** 3:  # 大于等于1GB/s
            return f"{bytes_per_sec / (1024 ** 3):.2f} GB/s"
        elif bytes_per_sec >= 1024 ** 2:  # 大于等于1MB/s
            return f"{bytes_per_sec / (1024 ** 2):.2f} MB/s"
        elif bytes_per_sec >= 1024:  # 大于等于1KB/s
            return f"{bytes_per_sec / 1024:.2f} KB/s"
        else:  # 小于1KB/s，使用字节/秒
            return f"{bytes_per_sec:.0f} B/s"

    def get_system_info(self) -> Dict[str, Any]:
        """
        获取详细的系统信息

        收集系统的全面信息，包括硬件配置、操作系统信息、网络接口等。
        这些信息用于监控摘要和系统状态报告。

        Returns:
            Dict[str, Any]: 包含系统详细信息的字典

        返回的信息包括：
        - cpu_count: CPU核心数（逻辑核心）
        - cpu_freq: CPU频率（MHz）
        - memory_total: 总内存大小（字节）
        - memory_available: 可用内存大小（字节）
        - disk_total: 总磁盘空间（字节）
        - disk_free: 可用磁盘空间（字节）
        - platform: 操作系统平台信息
        - python_version: Python版本
        - network_interfaces: 网络接口列表
        - boot_time: 系统启动时间
        """
        try:
            # 获取CPU信息
            cpu_count = psutil.cpu_count(logical=True)  # 逻辑核心数（包括超线程）
            cpu_freq = psutil.cpu_freq()  # CPU频率信息

            # 获取内存信息
            memory = psutil.virtual_memory()  # 虚拟内存信息

            # 获取磁盘信息（根目录）
            disk = psutil.disk_usage('/')  # 根目录磁盘使用情况

            # 获取网络接口信息
            net_if_addrs = psutil.net_if_addrs()  # 所有网络接口地址
            network_interfaces = []

            # 遍历所有网络接口，提取IPv4地址
            for interface, addrs in net_if_addrs.items():
                for addr in addrs:
                    # 检查是否为IPv4地址（family == 2表示IPv4）
                    if hasattr(addr, 'family') and addr.family == 2:
                        network_interfaces.append({
                            'interface': interface,  # 接口名称
                            'address': addr.address,  # IP地址
                            'netmask': addr.netmask  # 子网掩码
                        })
                        break  # 只取第一个IPv4地址

            # 构建系统信息字典
            return {
                'cpu_count': cpu_count,  # CPU核心数
                'cpu_freq': cpu_freq.current if cpu_freq else 0,  # CPU频率（MHz）
                'memory_total': memory.total,  # 总内存（字节）
                'memory_available': memory.available,  # 可用内存（字节）
                'disk_total': disk.total,  # 总磁盘空间（字节）
                'disk_free': disk.free,  # 可用磁盘空间（字节）
                'platform': platform.platform(),  # 操作系统平台信息
                'python_version': platform.python_version(),  # Python版本
                'network_interfaces': network_interfaces,  # 网络接口列表
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')  # 系统启动时间
            }
        except Exception as e:
            # 如果获取系统信息失败，记录错误并返回空字典
            self.logger.error(f"获取系统信息失败: {e}")
            return {}

    def check_alert_conditions(self, metric: str, value: float, threshold: float) -> bool:
        """
        检查是否需要发送警报

        智能警报系统，支持冷却时间机制，避免频繁警报。
        当监控指标超过阈值时，只有在冷却时间过后才会再次触发警报。

        Args:
            metric (str): 监控指标名称（如'cpu', 'memory', 'disk'）
            value (float): 当前监控值
            threshold (float): 警报阈值

        Returns:
            bool: True表示需要发送警报，False表示不需要

        工作原理：
        1. 生成唯一的警报键（metric_threshold）
        2. 检查是否在冷却时间内
        3. 如果超过阈值且不在冷却时间内，记录警报时间并返回True
        4. 否则返回False

        示例：
            check_alert_conditions('cpu', 85.0, 80.0) -> True（CPU使用率85%超过80%阈值）
            check_alert_conditions('cpu', 85.0, 80.0) -> False（在冷却时间内）
        """
        # 获取当前时间戳
        current_time = time.time()

        # 生成唯一的警报键（指标名称_阈值）
        alert_key = f"{metric}_{threshold}"

        # 检查冷却时间机制
        if alert_key in self.alert_history:
            # 获取上次警报时间
            last_alert_time = self.alert_history[alert_key]
            # 获取冷却时间配置（默认300秒）
            cooldown = self.config['alert_settings']['alert_cooldown_seconds']

            # 如果距离上次警报时间小于冷却时间，不发送警报
            if current_time - last_alert_time < cooldown:
                return False

        # 检查是否超过阈值
        if value > threshold:
            # 记录当前警报时间
            self.alert_history[alert_key] = current_time
            return True  # 需要发送警报

        return False  # 不需要发送警报

    def play_alert_sound(self):
        """
        播放警报声音

        跨平台声音警报系统，支持Windows、Linux和macOS。
        当监控指标超过阈值时，播放系统声音提醒用户。

        支持的平台：
        - Windows: 使用winsound.MessageBeep()播放系统默认警报声
        - Linux: 使用beep命令播放蜂鸣声
        - macOS: 使用afplay命令播放系统声音文件

        注意：
        - 需要确保声音警报功能已启用（enable_sound_alerts = True）
        - Linux系统需要安装beep包：sudo apt-get install beep
        - 如果播放失败，会记录警告日志但不影响监控功能
        """
        # 检查是否启用声音警报
        if not self.config['alert_settings']['enable_sound_alerts']:
            return  # 如果未启用，直接返回

        try:
            # 根据操作系统选择不同的声音播放方式
            if platform.system() == 'Windows':
                # Windows系统使用内置的警报声
                import winsound
                winsound.MessageBeep()  # 播放系统默认警报声

            elif platform.system() == 'Linux':
                # Linux系统使用beep命令（需要安装beep包）
                subprocess.run(['beep'], capture_output=True)

            elif platform.system() == 'Darwin':
                # macOS系统使用afplay命令播放系统声音
                subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'], capture_output=True)

        except Exception as e:
            # 如果播放声音失败，记录警告日志但不中断监控
            self.logger.warning(f"播放警报声音失败: {e}")

    def export_data_to_csv(self):
        """
        导出监控数据到CSV文件

        将收集的监控数据导出为CSV格式，便于后续分析和处理。
        支持导出CPU、内存、网络和磁盘的监控数据。

        导出功能：
        - 自动创建导出目录
        - 使用时间戳命名文件，避免覆盖
        - 支持UTF-8编码，确保中文正常显示
        - 包含详细的列标题和数据说明

        导出文件格式：
        - cpu_data_YYYYMMDD_HHMMSS.csv: CPU监控数据
        - memory_data_YYYYMMDD_HHMMSS.csv: 内存监控数据
        - network_data_YYYYMMDD_HHMMSS.csv: 网络监控数据
        - disk_data_YYYYMMDD_HHMMSS.csv: 磁盘监控数据

        注意：
        - 只有在启用CSV导出功能时才会执行
        - 如果数据历史为空，不会创建文件
        - 导出完成后会记录日志信息
        """
        # 检查是否启用CSV导出功能
        if not self.config['data_export']['enable_csv_export']:
            return  # 如果未启用，直接返回

        # 获取导出目录路径
        export_dir = self.config['data_export']['csv_directory']

        # 创建导出目录（如果不存在）
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            print(f"创建数据导出目录: {export_dir}")

        # 生成时间戳（用于文件名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 导出CPU监控数据
        if self.data_history['cpu']:
            cpu_file = f"{export_dir}/cpu_data_{timestamp}.csv"
            with open(cpu_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入CSV头部
                writer.writerow(['Timestamp', 'CPU_Percent', 'Core_Count'])
                # 写入数据行
                for data in self.data_history['cpu']:
                    writer.writerow([data['timestamp'], data['cpu_percent'], data['core_count']])
            print(f"CPU数据已导出: {cpu_file}")

        # 导出内存监控数据
        if self.data_history['memory']:
            memory_file = f"{export_dir}/memory_data_{timestamp}.csv"
            with open(memory_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入CSV头部
                writer.writerow(['Timestamp', 'Memory_Percent', 'Used_GB', 'Total_GB'])
                # 写入数据行
                for data in self.data_history['memory']:
                    writer.writerow([data['timestamp'], data['memory_percent'], data['used_gb'], data['total_gb']])
            print(f"内存数据已导出: {memory_file}")

        # 记录导出完成日志
        self.logger.info(f"监控数据已导出到 {export_dir} 目录")

    def monitor_cpu_enhanced(self, interval: float = None) -> None:
        """
        增强版CPU监控

        实时监控CPU使用情况，包括总体使用率和各核心使用率。
        支持CPU频率显示、数据历史记录、智能警报和日志记录。

        Args:
            interval (float, optional): 监控间隔时间（秒），默认从配置文件读取

        监控功能：
        - 总体CPU使用率监控
        - 各核心CPU使用率监控（可选）
        - CPU频率信息显示（如果可用）
        - 数据历史记录（最多1000个数据点）
        - 智能警报系统（支持冷却时间）
        - 声音警报提醒
        - 详细日志记录

        输出格式：
        - CPU总占用率: XX.X% | 核心数: X | 频率: XXXXMHz
        - 各核心占用率: 核心0: XX% | 核心1: XX% | ...

        异常处理：
        - KeyboardInterrupt: 用户按Ctrl+C停止监控
        - Exception: 其他异常，记录错误日志
        """
        # 设置监控间隔（如果未指定，从配置文件读取）
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录监控开始日志
        self.logger.info("开始增强版CPU监控")

        try:
            # 显示监控开始信息
            print("开始监控CPU使用情况")
            print("按 Ctrl+C 停止监控")
            print("-" * 60)

            # 主监控循环
            while self.monitoring:
                # 获取CPU使用率信息
                cpu_percent = psutil.cpu_percent(interval=interval)  # 总体CPU使用率
                core_count = psutil.cpu_count(logical=True)  # 逻辑核心数
                per_cpu = psutil.cpu_percent(interval=interval, percpu=True)  # 各核心使用率

                # 获取CPU频率信息（如果可用）
                cpu_freq = psutil.cpu_freq()
                freq_info = f" | 频率: {cpu_freq.current:.0f}MHz" if cpu_freq else ""

                # 格式化输出总体CPU信息
                print(f"CPU总占用率: {cpu_percent:5.1f}% | 核心数: {core_count}{freq_info}")

                # 显示各核心使用率（如果启用）
                if self.config['display_settings']['show_per_core_cpu']:
                    print("各核心占用率:", end=" ")
                    for i, core in enumerate(per_cpu):
                        # 格式化每个核心的使用率，最后一个核心不加分隔符
                        print(f"核心{i}: {core:3.0f}%", end=" | " if i < len(per_cpu) - 1 else "")
                    print()  # 换行

                # 记录数据到历史记录
                self.data_history['cpu'].append({
                    'timestamp': datetime.now(),  # 时间戳
                    'cpu_percent': cpu_percent,  # 总体CPU使用率
                    'core_count': core_count,  # 核心数
                    'per_cpu': per_cpu  # 各核心使用率
                })

                # 记录监控日志
                self.logger.info(f"CPU使用率: {cpu_percent:.1f}%")

                # 检查是否需要发送警报
                if self.check_alert_conditions('cpu', cpu_percent, self.config['cpu_warning_threshold']):
                    self.logger.warning(f"CPU使用率过高: {cpu_percent:.1f}%")
                    self.play_alert_sound()  # 播放警报声音

                # 等待下一个监控周期
                time.sleep(interval)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("CPU监控已停止")
            print("\nCPU监控已停止")
        except Exception as e:
            # 其他异常处理
            self.logger.error(f"CPU监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def monitor_memory_enhanced(self, interval: float = None) -> None:
        """
        增强版内存监控

        实时监控系统内存使用情况，包括物理内存和交换内存。
        支持内存使用率计算、数据历史记录、智能警报和日志记录。

        Args:
            interval (float, optional): 监控间隔时间（秒），默认从配置文件读取

        监控功能：
        - 物理内存使用率监控
        - 交换内存使用率监控（如果存在）
        - 内存容量信息显示（总量、已用、可用）
        - 数据历史记录（最多1000个数据点）
        - 智能警报系统（支持冷却时间）
        - 声音警报提醒
        - 详细日志记录

        输出格式：
        - 内存使用率: XX.X% | 总量: XX.XGB | 已用: XX.XGB | 可用: XX.XGB
        - 交换内存: XX.X% | 总量: XX.XGB | 已用: XX.XGB（如果存在）

        异常处理：
        - KeyboardInterrupt: 用户按Ctrl+C停止监控
        - Exception: 其他异常，记录错误日志
        """
        # 设置监控间隔（如果未指定，从配置文件读取）
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录监控开始日志
        self.logger.info("开始增强版内存监控")

        try:
            # 显示监控开始信息
            print("开始监控内存使用情况")
            print("按 Ctrl+C 停止监控")
            print("-" * 60)

            # 主监控循环
            while self.monitoring:
                # 获取内存信息
                memory = psutil.virtual_memory()  # 物理内存信息
                swap = psutil.swap_memory()  # 交换内存信息

                # 计算物理内存使用情况（转换为GB）
                total_gb = memory.total / (1024 ** 3)  # 总内存（GB）
                used_gb = memory.used / (1024 ** 3)  # 已用内存（GB）
                available_gb = memory.available / (1024 ** 3)  # 可用内存（GB）
                memory_percent = memory.percent  # 内存使用率（百分比）

                # 计算交换内存使用情况（转换为GB）
                swap_total_gb = swap.total / (1024 ** 3)  # 总交换内存（GB）
                swap_used_gb = swap.used / (1024 ** 3)  # 已用交换内存（GB）
                swap_percent = swap.percent  # 交换内存使用率（百分比）

                # 格式化输出物理内存信息
                print(f"内存使用率: {memory_percent:5.1f}% | "
                      f"总量: {total_gb:6.1f}GB | "
                      f"已用: {used_gb:6.1f}GB | "
                      f"可用: {available_gb:6.1f}GB")

                # 显示交换内存信息（如果存在）
                if swap_total_gb > 0:
                    print(f"交换内存: {swap_percent:5.1f}% | "
                          f"总量: {swap_total_gb:6.1f}GB | "
                          f"已用: {swap_used_gb:6.1f}GB")

                # 记录数据到历史记录
                self.data_history['memory'].append({
                    'timestamp': datetime.now(),  # 时间戳
                    'memory_percent': memory_percent,  # 物理内存使用率
                    'used_gb': used_gb,  # 已用物理内存（GB）
                    'total_gb': total_gb,  # 总物理内存（GB）
                    'swap_percent': swap_percent,  # 交换内存使用率
                    'swap_used_gb': swap_used_gb,  # 已用交换内存（GB）
                    'swap_total_gb': swap_total_gb  # 总交换内存（GB）
                })

                # 记录监控日志
                self.logger.info(f"内存使用率: {memory_percent:.1f}%, 已用: {used_gb:.1f}GB/{total_gb:.1f}GB")

                # 检查是否需要发送警报
                if self.check_alert_conditions('memory', memory_percent, self.config['memory_warning_threshold']):
                    self.logger.warning(f"内存使用率过高: {memory_percent:.1f}%")
                    self.play_alert_sound()  # 播放警报声音

                # 等待下一个监控周期
                time.sleep(interval)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("内存监控已停止")
            print("\n内存监控已停止")
        except Exception as e:
            # 其他异常处理
            self.logger.error(f"内存监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def monitor_network_enhanced(self, interval: float = None) -> None:
        """
        增强版网络监控

        实时监控网络使用情况，包括上传和下载速度。
        支持网络接口信息显示、数据历史记录、智能警报和日志记录。

        Args:
            interval (float, optional): 监控间隔时间（秒），默认从配置文件读取

        监控功能：
        - 网络上传速度监控
        - 网络下载速度监控
        - 网络接口信息显示（可选）
        - 数据历史记录（最多1000个数据点）
        - 智能警报系统（支持冷却时间）
        - 声音警报提醒
        - 详细日志记录

        工作原理：
        1. 获取初始网络统计信息
        2. 等待一个监控间隔
        3. 获取当前网络统计信息
        4. 计算速度差值（字节/秒）
        5. 格式化显示速度信息

        输出格式：
        - 上传速度: XX.XX MB/s | 下载速度: XX.XX MB/s
        - 活跃接口: eth0, wlan0, lo（可选）

        异常处理：
        - KeyboardInterrupt: 用户按Ctrl+C停止监控
        - Exception: 其他异常，记录错误日志
        """
        # 设置监控间隔（如果未指定，从配置文件读取）
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录监控开始日志
        self.logger.info("开始增强版网络监控")

        try:
            # 显示监控开始信息
            print("开始监控网络使用情况")
            print("正在初始化网络统计...")
            print("按 Ctrl+C 停止监控")
            print("-" * 60)

            # 获取初始网络统计信息
            net_io = psutil.net_io_counters()
            last_bytes_sent = net_io.bytes_sent  # 初始发送字节数
            last_bytes_recv = net_io.bytes_recv  # 初始接收字节数
            last_time = time.time()  # 初始时间戳

            # 记录初始化完成日志
            self.logger.info("网络统计初始化完成")

            # 等待一个监控间隔，确保有足够的时间差来计算速度
            time.sleep(interval)

            # 主监控循环
            while self.monitoring:
                # 获取当前网络统计信息
                net_io = psutil.net_io_counters()
                current_bytes_sent = net_io.bytes_sent  # 当前发送字节数
                current_bytes_recv = net_io.bytes_recv  # 当前接收字节数
                current_time = time.time()  # 当前时间戳

                # 计算速度差值
                time_diff = current_time - last_time  # 时间差（秒）
                bytes_sent_diff = current_bytes_sent - last_bytes_sent  # 发送字节差
                bytes_recv_diff = current_bytes_recv - last_bytes_recv  # 接收字节差

                # 计算网络速度（字节/秒）
                upload_speed = bytes_sent_diff / time_diff  # 上传速度
                download_speed = bytes_recv_diff / time_diff  # 下载速度

                # 获取网络接口信息
                net_if_addrs = psutil.net_if_addrs()
                active_interfaces = []

                # 遍历所有网络接口，找出活跃的IPv4接口
                for interface, addrs in net_if_addrs.items():
                    for addr in addrs:
                        # 检查是否为IPv4地址且不是回环地址
                        if (hasattr(addr, 'family') and
                                addr.family == 2 and
                                not addr.address.startswith('127.')):
                            active_interfaces.append(interface)
                            break  # 只取第一个IPv4地址

                # 格式化输出网络速度信息
                print(f"上传速度: {self.format_speed(upload_speed):>10} | "
                      f"下载速度: {self.format_speed(download_speed):>10}")

                # 显示活跃网络接口（如果启用）
                if self.config['display_settings']['show_network_interfaces']:
                    print(f"活跃接口: {', '.join(active_interfaces[:3])}")  # 只显示前3个接口

                # 记录数据到历史记录
                self.data_history['network'].append({
                    'timestamp': datetime.now(),  # 时间戳
                    'upload_speed': upload_speed,  # 上传速度
                    'download_speed': download_speed,  # 下载速度
                    'total_sent': current_bytes_sent,  # 总发送字节数
                    'total_recv': current_bytes_recv,  # 总接收字节数
                    'active_interfaces': active_interfaces  # 活跃接口列表
                })

                # 记录监控日志
                self.logger.info(
                    f"网络速度 - 上传: {self.format_speed(upload_speed)}, 下载: {self.format_speed(download_speed)}")

                # 检查是否需要发送警报（上传或下载速度超过阈值）
                if (self.check_alert_conditions('network_upload', upload_speed, self.config['network_speed_warning']) or
                        self.check_alert_conditions('network_download', download_speed,
                                                    self.config['network_speed_warning'])):
                    self.logger.warning(
                        f"网络速度异常 - 上传: {self.format_speed(upload_speed)}, 下载: {self.format_speed(download_speed)}")
                    self.play_alert_sound()  # 播放警报声音

                # 更新上一次的值，为下次计算做准备
                last_bytes_sent = current_bytes_sent
                last_bytes_recv = current_bytes_recv
                last_time = current_time

                # 等待下一个监控周期
                time.sleep(interval)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("网络监控已停止")
            print("\n网络监控已停止")
        except Exception as e:
            # 其他异常处理
            self.logger.error(f"网络监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def monitor_disk_enhanced(self, interval: float = None) -> None:
        """
        增强版磁盘监控

        实时监控所有磁盘分区的使用情况，包括使用率、容量信息等。
        支持多分区监控、数据历史记录、智能警报和日志记录。

        Args:
            interval (float, optional): 监控间隔时间（秒），默认从配置文件读取

        监控功能：
        - 所有磁盘分区使用率监控
        - 磁盘容量信息显示（总量、已用、可用）
        - 数据历史记录（最多1000个数据点）
        - 智能警报系统（支持冷却时间）
        - 声音警报提醒
        - 详细日志记录
        - 异常分区处理（跳过无法访问的分区）

        输出格式：
        - 分区: /dev/sda1 | 挂载点: / | 使用率: XX.X% | 已用: XX.XGB | 可用: XX.XGB | 总量: XX.XGB

        异常处理：
        - KeyboardInterrupt: 用户按Ctrl+C停止监控
        - Exception: 其他异常，记录错误日志
        - 单个分区异常：跳过该分区，继续监控其他分区
        """
        # 设置监控间隔（如果未指定，从配置文件读取）
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录监控开始日志
        self.logger.info("开始增强版磁盘监控")

        try:
            # 显示监控开始信息
            print("开始监控磁盘使用情况")
            print("按 Ctrl+C 停止监控")
            print("-" * 60)

            # 主监控循环
            while self.monitoring:
                # 获取所有磁盘分区信息
                disk_partitions = psutil.disk_partitions()

                # 遍历每个磁盘分区
                for partition in disk_partitions:
                    try:
                        # 获取磁盘使用情况
                        disk_usage = psutil.disk_usage(partition.mountpoint)

                        # 计算磁盘使用率（百分比）
                        disk_percent = (disk_usage.used / disk_usage.total) * 100

                        # 计算磁盘容量信息（转换为GB）
                        disk_total_gb = disk_usage.total / (1024 ** 3)  # 总容量（GB）
                        disk_used_gb = disk_usage.used / (1024 ** 3)  # 已用容量（GB）
                        disk_free_gb = disk_usage.free / (1024 ** 3)  # 可用容量（GB）

                        # 格式化输出磁盘信息
                        print(f"分区: {partition.device} | "
                              f"挂载点: {partition.mountpoint} | "
                              f"使用率: {disk_percent:5.1f}% | "
                              f"已用: {disk_used_gb:6.1f}GB | "
                              f"可用: {disk_free_gb:6.1f}GB | "
                              f"总量: {disk_total_gb:6.1f}GB")

                        # 记录数据到历史记录
                        self.data_history['disk'].append({
                            'timestamp': datetime.now(),  # 时间戳
                            'device': partition.device,  # 设备名称
                            'mountpoint': partition.mountpoint,  # 挂载点
                            'disk_percent': disk_percent,  # 使用率（百分比）
                            'used_gb': disk_used_gb,  # 已用容量（GB）
                            'total_gb': disk_total_gb,  # 总容量（GB）
                            'free_gb': disk_free_gb  # 可用容量（GB）
                        })

                        # 检查是否需要发送警报
                        if self.check_alert_conditions('disk', disk_percent, self.config['disk_warning_threshold']):
                            self.logger.warning(f"磁盘使用率过高: {partition.device} - {disk_percent:.1f}%")
                            self.play_alert_sound()  # 播放警报声音

                    except Exception as e:
                        # 如果某个分区无法访问，记录警告但继续监控其他分区
                        self.logger.warning(f"无法获取分区 {partition.device} 的信息: {e}")

                # 显示分隔线
                print("-" * 60)

                # 等待下一个监控周期
                time.sleep(interval)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("磁盘监控已停止")
            print("\n磁盘监控已停止")
        except Exception as e:
            # 其他异常处理
            self.logger.error(f"磁盘监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def start_comprehensive_monitoring(self, interval: float = None) -> None:
        """
        开始综合监控（多线程）

        启动多线程综合监控，同时监控CPU、内存、网络和磁盘。
        每个监控项目在独立的线程中运行，互不干扰。

        Args:
            interval (float, optional): 监控间隔时间（秒），默认从配置文件读取

        监控线程：
        - CPU-Monitor: CPU使用率监控线程
        - Memory-Monitor: 内存使用率监控线程
        - Network-Monitor: 网络速度监控线程
        - Disk-Monitor: 磁盘使用率监控线程
        - Data-Export: 数据导出线程（可选）

        主线程功能：
        - 显示实时运行时间
        - 处理用户中断信号（Ctrl+C）
        - 协调所有监控线程

        线程特性：
        - 所有线程设置为守护线程（daemon=True）
        - 主线程退出时，所有子线程自动结束
        - 支持优雅停止（通过self.monitoring标志）

        异常处理：
        - KeyboardInterrupt: 用户按Ctrl+C停止监控
        - 自动调用stop_monitoring()进行清理
        """
        # 设置监控间隔（如果未指定，从配置文件读取）
        if interval is None:
            interval = self.config['monitor_interval']

        # 设置监控状态为开始
        self.monitoring = True

        # 记录监控开始时间
        self.start_time = datetime.now()

        # 记录监控开始日志
        self.logger.info("开始综合系统监控")

        # 显示监控开始信息
        print("开始综合系统监控")
        print("按 Ctrl+C 停止监控")
        print("=" * 80)

        # 创建监控线程列表
        threads = [
            # CPU监控线程
            threading.Thread(target=self.monitor_cpu_enhanced, args=(interval,), name="CPU-Monitor"),
            # 内存监控线程
            threading.Thread(target=self.monitor_memory_enhanced, args=(interval,), name="Memory-Monitor"),
            # 网络监控线程
            threading.Thread(target=self.monitor_network_enhanced, args=(interval,), name="Network-Monitor"),
            # 磁盘监控线程
            threading.Thread(target=self.monitor_disk_enhanced, args=(interval,), name="Disk-Monitor")
        ]

        # 启动所有监控线程
        for thread in threads:
            thread.daemon = True  # 设置为守护线程
            thread.start()  # 启动线程
            self.monitor_threads.append(thread)  # 添加到线程列表

        # 创建数据导出线程（如果启用）
        if self.config['data_export']['enable_csv_export']:
            export_thread = threading.Thread(target=self._export_data_periodically, name="Data-Export")
            export_thread.daemon = True  # 设置为守护线程
            export_thread.start()  # 启动线程
            self.monitor_threads.append(export_thread)  # 添加到线程列表

        try:
            # 主线程显示运行时间
            while self.monitoring:
                if self.start_time:
                    # 计算并显示运行时间
                    runtime = datetime.now() - self.start_time
                    print(f"\r运行时间: {runtime}", end="", flush=True)
                time.sleep(1)  # 每秒更新一次运行时间

        except KeyboardInterrupt:
            # 用户按Ctrl+C，停止监控
            self.stop_monitoring()

    def _export_data_periodically(self):
        """
        定期导出数据

        在后台线程中定期导出监控数据到CSV文件。
        根据配置的导出间隔自动执行数据导出操作。

        工作流程：
        1. 等待指定的导出间隔时间
        2. 检查监控状态是否仍在运行
        3. 如果仍在运行，执行数据导出
        4. 重复上述过程

        注意事项：
        - 这是一个私有方法，仅供内部使用
        - 在独立的守护线程中运行
        - 支持优雅停止（通过self.monitoring标志）
        - 避免在监控停止时执行导出操作
        """
        # 获取导出间隔时间（从配置文件读取）
        export_interval = self.config['data_export']['export_interval']

        # 定期导出循环
        while self.monitoring:
            # 等待指定的导出间隔时间
            time.sleep(export_interval)

            # 再次检查监控状态，避免在停止时导出
            if self.monitoring:
                self.export_data_to_csv()  # 执行数据导出

    def stop_monitoring(self) -> None:
        """
        停止监控

        优雅地停止所有监控线程，并执行清理操作。
        包括等待线程结束、导出最终数据、显示统计信息等。

        停止流程：
        1. 设置监控状态为False，通知所有线程停止
        2. 等待所有监控线程结束（最多等待5秒）
        3. 导出最终监控数据到CSV文件
        4. 显示监控统计信息（运行时间、数据点数量等）
        5. 记录停止日志

        统计信息包括：
        - 总运行时间
        - 各监控指标的数据点数量
        - 触发的警报次数

        注意事项：
        - 使用timeout=5确保不会无限等待
        - 即使线程未正常结束也会继续执行清理
        - 在监控停止时也会导出数据
        """
        # 设置监控状态为False，通知所有线程停止
        self.monitoring = False

        # 等待所有监控线程结束
        for thread in self.monitor_threads:
            if thread.is_alive():
                # 等待线程结束，最多等待5秒
                thread.join(timeout=5)

        # 导出最终监控数据
        self.export_data_to_csv()

        # 显示监控运行统计信息
        if self.start_time:
            # 计算总运行时间
            total_runtime = datetime.now() - self.start_time
            print(f"\n监控已停止，总运行时间: {total_runtime}")

            # 显示各监控指标的数据点数量
            print(f"收集的数据点:")
            for metric, data in self.data_history.items():
                print(f"  {metric}: {len(data)} 个数据点")

        # 记录监控停止日志
        self.logger.info("综合监控已停止")

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """
        获取监控摘要

        生成详细的监控摘要报告，包括运行时间、数据统计、系统信息等。
        用于监控结束后的数据分析和报告生成。

        Returns:
            Dict[str, Any]: 包含监控摘要的字典

        摘要内容包括：
        - start_time: 监控开始时间
        - total_runtime: 总运行时间
        - data_points: 各监控指标的数据点数量
        - alerts_triggered: 触发的警报次数
        - system_info: 系统信息
        - {metric}_stats: 各监控指标的统计信息（最小值、最大值、平均值）

        统计指标：
        - cpu_stats: CPU使用率统计
        - memory_stats: 内存使用率统计
        - network_stats: 网络速度统计（上传+下载）
        - disk_stats: 磁盘使用率统计

        使用示例：
            summary = monitor.get_monitoring_summary()
            print(f"CPU平均使用率: {summary['cpu_stats']['avg']:.1f}%")
            print(f"总运行时间: {summary['total_runtime']}")
        """
        # 构建基础摘要信息
        summary = {
            'start_time': self.start_time,  # 监控开始时间
            'total_runtime': datetime.now() - self.start_time if self.start_time else None,  # 总运行时间
            'data_points': {metric: len(data) for metric, data in self.data_history.items()},  # 数据点数量
            'alerts_triggered': len(self.alert_history),  # 触发的警报次数
            'system_info': self.get_system_info()  # 系统信息
        }

        # 计算各监控指标的统计数据
        for metric, data in self.data_history.items():
            if data:  # 确保有数据才进行统计
                # 根据监控指标类型提取相应的数值
                if metric == 'cpu':
                    # CPU使用率数据
                    values = [d['cpu_percent'] for d in data]
                elif metric == 'memory':
                    # 内存使用率数据
                    values = [d['memory_percent'] for d in data]
                elif metric == 'network':
                    # 网络总速度数据（上传+下载）
                    values = [d['upload_speed'] + d['download_speed'] for d in data]
                elif metric == 'disk':
                    # 磁盘使用率数据
                    values = [d['disk_percent'] for d in data]
                else:
                    # 跳过未知的监控指标
                    continue

                # 计算统计信息（最小值、最大值、平均值）
                summary[f'{metric}_stats'] = {
                    'min': min(values),  # 最小值
                    'max': max(values),  # 最大值
                    'avg': sum(values) / len(values)  # 平均值
                }

        return summary


def main():
    """
    主函数 - 增强版系统监控工具入口

    程序启动入口，负责初始化、用户交互和监控流程控制。

    程序流程：
    1. 检查并安装必要的依赖（psutil）
    2. 创建监控器实例
    3. 显示系统基本信息
    4. 提供监控模式选择
    5. 启动相应的监控功能
    6. 处理用户中断并显示监控摘要

    监控模式：
    - 1-4: 单项监控（实际都启动综合监控）
    - 5: 综合监控（推荐）
    - 其他: 默认启动综合监控

    异常处理：
    - ImportError: 自动安装缺失的依赖
    - KeyboardInterrupt: 优雅停止监控并显示摘要
    - 其他异常: 记录错误日志

    使用说明：
    - 运行程序后按提示选择监控模式
    - 按Ctrl+C停止监控
    - 监控结束后会显示统计摘要
    """
    # 检查并安装必要的依赖
    try:
        import psutil
    except ImportError:
        # 如果psutil未安装，自动安装
        import sys
        import subprocess
        print("正在安装必要的依赖包...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
        print("依赖包安装完成！")

    # 创建增强版系统监控器实例
    monitor = EnhancedSystemMonitor()

    # 显示系统基本信息
    system_info = monitor.get_system_info()
    if system_info:
        print("系统信息:")
        print(f"CPU核心数: {system_info.get('cpu_count', 'N/A')}")
        print(f"CPU频率: {system_info.get('cpu_freq', 0):.0f} MHz")
        print(f"内存总量: {monitor.format_bytes(system_info.get('memory_total', 0))}")
        print(f"磁盘总量: {monitor.format_bytes(system_info.get('disk_total', 0))}")
        print(f"平台: {system_info.get('platform', 'N/A')}")
        print(f"启动时间: {system_info.get('boot_time', 'N/A')}")
        print("-" * 60)

    # 提供监控模式选择
    print("请选择监控模式:")
    print("1. CPU监控")
    print("2. 内存监控")
    print("3. 网络监控")
    print("4. 磁盘监控")
    print("5. 综合监控（推荐）")

    # 获取用户选择
    choice = input("请输入选择 (1/2/3/4/5): ").strip()

    try:
        # 根据用户选择启动相应的监控模式
        # 注意：目前所有选择都启动综合监控，可以根据需要修改
        if choice == "1":
            monitor.start_comprehensive_monitoring()
        elif choice == "2":
            monitor.start_comprehensive_monitoring()
        elif choice == "3":
            monitor.start_comprehensive_monitoring()
        elif choice == "4":
            monitor.start_comprehensive_monitoring()
        elif choice == "5":
            monitor.start_comprehensive_monitoring()
        else:
            print("无效选择，启动综合监控")
            monitor.start_comprehensive_monitoring()

    except KeyboardInterrupt:
        # 用户按Ctrl+C停止监控
        print("\n正在停止监控...")
        monitor.stop_monitoring()

        # 显示监控摘要
        summary = monitor.get_monitoring_summary()
        if summary:
            print("\n监控摘要:")
            print(f"总运行时间: {summary['total_runtime']}")
            print(f"数据点数量:")
            for metric, count in summary['data_points'].items():
                print(f"  {metric}: {count}")
            print(f"触发警报次数: {summary['alerts_triggered']}")


# 程序入口点
if __name__ == "__main__":
    main()