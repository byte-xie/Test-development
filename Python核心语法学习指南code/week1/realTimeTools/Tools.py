# =============================================================================
# 系统监控工具 - 实时监控系统资源使用情况
#
# 功能特性：
# - CPU使用率监控（包括每个核心的详细使用率）
# - 内存使用情况监控（包括交换内存）
# - 网络速度监控（上传/下载速度）
# - 磁盘使用情况监控
# - 进程监控（显示占用资源最多的进程）
# - 智能警报系统（可配置阈值）
# - 日志记录和文件输出
# - 配置文件支持
#
# 作者：谢浩亮
# 版本：2.0 (优化版)
# 日期：2024年
# =============================================================================

# 导入必要的库
import psutil  # 用于获取系统和进程信息
import time  # 用于时间相关操作
import logging  # 用于日志记录
import os  # 用于文件和目录操作
import threading  # 用于多线程支持
from datetime import datetime  # 用于时间戳
from typing import Optional, Dict, Any, List  # 类型提示
import json  # 用于配置文件处理


class SystemMonitor:
    """
    系统监控器类 - 统一管理各种监控功能

    这个类提供了完整的系统监控功能，包括：
    - 配置管理：从JSON文件加载配置
    - 日志管理：统一的日志记录系统
    - 监控功能：CPU、内存、网络、磁盘、进程监控
    - 警报系统：可配置的阈值警报
    - 数据格式化：友好的数据展示格式

    使用示例：
        monitor = SystemMonitor()
        monitor.start_monitoring("cpu")  # 开始CPU监控
        monitor.start_monitoring("system")  # 开始综合监控
    """

    def __init__(self, log_dir: str = 'logs', config_file: str = 'monitor_config.json'):
        """
        初始化系统监控器

        Args:
            log_dir (str): 日志文件存储目录，默认为'logs'
            config_file (str): 配置文件路径，默认为'monitor_config.json'

        初始化过程：
        1. 设置日志目录和配置文件路径
        2. 加载配置文件（如果存在）
        3. 设置日志系统
        4. 初始化监控状态
        """
        # 存储日志目录路径
        self.log_dir = log_dir
        # 存储配置文件路径
        self.config_file = config_file
        # 日志记录器实例（初始为None）
        self.logger = None
        # 加载配置文件，获取监控参数
        self.config = self._load_config()
        # 设置日志系统
        self._setup_logging()
        # 监控状态标志（False表示未开始监控）
        self.monitoring = False
        # 监控线程对象（用于多线程监控）
        self.monitor_thread = None

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        从JSON配置文件中加载监控参数，如果配置文件不存在或加载失败，
        则使用默认配置。这样可以避免硬编码参数，提高灵活性。

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
        """
        # 默认配置参数（当配置文件不存在时使用）
        default_config = {
            "cpu_warning_threshold": 80,  # CPU使用率超过80%时发出警告
            "memory_warning_threshold": 80,  # 内存使用率超过80%时发出警告
            "disk_warning_threshold": 90,  # 磁盘使用率超过90%时发出警告
            "network_speed_warning": 100 * 1024 * 1024,  # 网络速度超过100MB/s时发出警告
            "process_cpu_warning": 50,  # 进程CPU使用率超过50%时发出警告
            "process_memory_warning": 10,  # 进程内存使用率超过10%时发出警告
            "monitor_interval": 1,  # 监控间隔为1秒
            "log_level": "INFO",  # 日志级别为INFO
            "enable_console_output": True,  # 启用控制台输出
            "enable_file_output": True  # 启用文件输出
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

    def _setup_logging(self):
        """
        配置日志系统（只配置一次）

        设置统一的日志记录系统，支持同时输出到文件和控制台。
        日志文件名包含日期，便于按日期管理日志文件。

        Returns:
            logging.Logger: 配置好的日志记录器

        日志配置说明：
        - 日志格式：时间 - 级别 - 消息
        - 时间格式：YYYY-MM-DD HH:MM:SS
        - 文件输出：logs/system_monitor_YYYYMMDD.log
        - 控制台输出：实时显示日志信息
        - 编码：UTF-8（支持中文）
        """
        # 如果日志记录器已经存在，直接返回（避免重复配置）
        if self.logger is not None:
            return self.logger

        # 创建日志目录（如果不存在）
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"创建日志目录: {self.log_dir}")

        # 定义日志格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'  # 时间 - 级别 - 消息
        date_format = '%Y-%m-%d %H:%M:%S'  # 时间格式：年-月-日 时:分:秒

        # 创建日志记录器实例
        self.logger = logging.getLogger('SystemMonitor')
        # 设置日志级别（从配置中读取）
        self.logger.setLevel(getattr(logging, self.config['log_level']))

        # 清除现有的处理器（避免重复添加）
        self.logger.handlers.clear()

        # 添加文件处理器（如果启用文件输出）
        if self.config['enable_file_output']:
            # 生成日志文件名，包含当前日期
            log_filename = f'{self.log_dir}/system_monitor_{datetime.now().strftime("%Y%m%d")}.log'
            # 创建文件处理器，使用UTF-8编码
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            # 设置日志格式
            file_handler.setFormatter(logging.Formatter(log_format, date_format))
            # 添加到日志记录器
            self.logger.addHandler(file_handler)
            print(f"日志文件输出已启用: {log_filename}")

        # 添加控制台处理器（如果启用控制台输出）
        if self.config['enable_console_output']:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            # 设置日志格式
            console_handler.setFormatter(logging.Formatter(log_format, date_format))
            # 添加到日志记录器
            self.logger.addHandler(console_handler)
            print("控制台日志输出已启用")

        return self.logger

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
        获取系统基本信息

        收集当前系统的基本硬件和软件信息，包括CPU、内存、平台等。
        这些信息用于显示系统概况和帮助用户了解系统配置。

        Returns:
            Dict[str, Any]: 包含系统信息的字典，如果获取失败返回空字典

        返回的信息包括：
        - cpu_count: CPU核心数（逻辑核心）
        - cpu_freq: CPU频率（MHz）
        - memory_total: 总内存大小（字节）
        - platform: 操作系统平台
        - python_version: Python版本信息
        """
        try:
            # 获取CPU核心数（包括逻辑核心）
            cpu_count = psutil.cpu_count(logical=True)

            # 获取CPU频率信息
            cpu_freq = psutil.cpu_freq()

            # 获取内存信息
            memory = psutil.virtual_memory()

            # 构建系统信息字典
            system_info = {
                'cpu_count': cpu_count,  # CPU核心数
                'cpu_freq': cpu_freq.current if cpu_freq else 0,  # CPU频率（MHz）
                'memory_total': memory.total,  # 总内存（字节）
                'platform': psutil.sys.platform,  # 操作系统平台
                'python_version': psutil.sys.version  # Python版本
            }

            return system_info

        except Exception as e:
            # 如果获取系统信息失败，记录错误并返回空字典
            self.logger.error(f"获取系统信息失败: {e}")
            return {}

    def monitor_cpu_usage(self, interval: float = None) -> None:
        """
        实时监控CPU占用率

        持续监控系统CPU的使用情况，包括总体使用率和每个核心的详细使用率。
        当CPU使用率超过配置的阈值时，会记录警告日志。

        Args:
            interval (float, optional): 监控间隔时间（秒），如果为None则使用配置文件中的值

        监控内容：
        - CPU总体使用率（百分比）
        - CPU核心数量
        - 每个核心的使用率
        - 警告阈值检查

        输出格式：
        - 控制台：实时显示CPU使用情况
        - 日志文件：记录监控数据和警告信息
        """
        # 如果没有指定间隔时间，使用配置文件中的默认值
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录开始监控的日志
        self.logger.info("开始CPU监控")

        try:
            # 显示监控开始信息
            print("开始监控CPU占用率")
            print("按 Ctrl+C 停止监控")
            print("-" * 50)  # 分隔线

            # 主监控循环
            while self.monitoring:
                # 获取CPU总体使用率（指定间隔时间内的平均值）
                cpu_percent = psutil.cpu_percent(interval=interval)

                # 获取CPU核心数量（逻辑核心）
                core_count = psutil.cpu_count(logical=True)

                # 获取每个核心的使用率
                per_cpu = psutil.cpu_percent(interval=interval, percpu=True)

                # 格式化输出总体CPU使用率
                print(f"CPU总占用率: {cpu_percent:5.1f}% | 核心数: {core_count}")

                # 显示每个核心的使用率
                print("各核心占用率:", end=" ")
                for i, core in enumerate(per_cpu):
                    # 格式化每个核心的使用率，最后一个核心不添加分隔符
                    print(f"核心{i}: {core:3.0f}%", end=" | " if i < len(per_cpu) - 1 else "")
                print()  # 换行

                # 记录CPU使用率到日志文件
                self.logger.info(f"CPU使用率: {cpu_percent:.1f}%")

                # 检查CPU使用率是否超过警告阈值
                if cpu_percent > self.config['cpu_warning_threshold']:
                    self.logger.warning(f"CPU使用率过高: {cpu_percent:.1f}%")

                # 短暂休眠，减轻CPU循环压力
                time.sleep(0.1)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("CPU监控已停止")
            print("\nCPU监控已停止")
        except Exception as e:
            # 监控过程中出现异常
            self.logger.error(f"CPU监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def monitor_memory_usage(self, interval: float = None) -> None:
        """
        实时监控内存使用情况

        持续监控系统内存的使用情况，包括使用率、总量、已用量和可用量。
        当内存使用率超过配置的阈值时，会记录警告日志。

        Args:
            interval (float, optional): 监控间隔时间（秒），如果为None则使用配置文件中的值

        监控内容：
        - 内存使用率（百分比）
        - 内存总量（GB）
        - 已使用内存（GB）
        - 可用内存（GB）
        - 警告阈值检查

        输出格式：
        - 控制台：实时显示内存使用情况
        - 日志文件：记录监控数据和警告信息
        """
        # 如果没有指定间隔时间，使用配置文件中的默认值
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录开始监控的日志
        self.logger.info("开始内存监控")

        try:
            # 显示监控开始信息
            print("开始监控内存使用情况")
            print("按 Ctrl+C 停止监控")
            print("-" * 50)  # 分隔线

            # 主监控循环
            while self.monitoring:
                # 获取系统内存信息
                memory = psutil.virtual_memory()

                # 计算内存使用情况的各个指标
                total_gb = memory.total / (1024 ** 3)  # 总内存（GB）
                used_gb = memory.used / (1024 ** 3)  # 已使用内存（GB）
                available_gb = memory.available / (1024 ** 3)  # 可用内存（GB）
                memory_percent = memory.percent  # 内存使用率（百分比）

                # 格式化输出内存使用情况
                print(f"内存使用率: {memory_percent:5.1f}% | "
                      f"总量: {total_gb:6.1f}GB | "
                      f"已用: {used_gb:6.1f}GB | "
                      f"可用: {available_gb:6.1f}GB")

                # 记录内存使用情况到日志文件
                self.logger.info(f"内存使用率: {memory_percent:.1f}%, 已用: {used_gb:.1f}GB/{total_gb:.1f}GB")

                # 检查内存使用率是否超过警告阈值
                if memory_percent > self.config['memory_warning_threshold']:
                    self.logger.warning(f"内存使用率过高: {memory_percent:.1f}%")

                # 按配置的间隔时间休眠
                time.sleep(interval)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("内存监控已停止")
            print("\n内存监控已停止")
        except Exception as e:
            # 监控过程中出现异常
            self.logger.error(f"内存监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def monitor_network_speed(self, interval: float = None) -> None:
        """
        实时监控网络速度

        持续监控系统的网络使用情况，包括上传速度、下载速度和活跃的网络接口。
        通过比较相邻时间点的网络统计信息来计算实时网络速度。
        当网络速度超过配置的阈值时，会记录警告日志。

        Args:
            interval (float, optional): 监控间隔时间（秒），如果为None则使用配置文件中的值

        监控内容：
        - 网络上传速度（字节/秒）
        - 网络下载速度（字节/秒）
        - 活跃网络接口
        - 警告阈值检查

        工作原理：
        1. 获取初始网络统计信息
        2. 等待一个间隔时间
        3. 获取当前网络统计信息
        4. 计算时间差和字节差
        5. 计算网络速度（字节差/时间差）

        输出格式：
        - 控制台：实时显示网络速度
        - 日志文件：记录监控数据和警告信息
        """
        # 如果没有指定间隔时间，使用配置文件中的默认值
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录开始监控的日志
        self.logger.info("开始网络速度监控")

        try:
            # 显示监控开始信息
            print("开始监控网络速度")
            print("正在初始化网络统计...")
            print("按 Ctrl+C 停止监控")
            print("-" * 50)  # 分隔线

            # 获取初始网络统计信息
            net_io = psutil.net_io_counters()
            last_bytes_sent = net_io.bytes_sent  # 初始发送字节数
            last_bytes_recv = net_io.bytes_recv  # 初始接收字节数
            last_time = time.time()  # 初始时间戳

            # 记录初始化完成日志
            self.logger.info("网络统计初始化完成")

            # 等待一个间隔时间，为第一次速度计算做准备
            time.sleep(interval)

            # 主监控循环
            while self.monitoring:
                # 获取当前网络统计信息
                net_io = psutil.net_io_counters()
                current_bytes_sent = net_io.bytes_sent  # 当前发送字节数
                current_bytes_recv = net_io.bytes_recv  # 当前接收字节数
                current_time = time.time()  # 当前时间戳

                # 计算时间差和字节差
                time_diff = current_time - last_time  # 时间差（秒）
                bytes_sent_diff = current_bytes_sent - last_bytes_sent  # 发送字节差
                bytes_recv_diff = current_bytes_recv - last_bytes_recv  # 接收字节差

                # 计算网络速度（字节/秒）
                upload_speed = bytes_sent_diff / time_diff  # 上传速度
                download_speed = bytes_recv_diff / time_diff  # 下载速度

                # 获取网络接口信息
                net_if_addrs = psutil.net_if_addrs()
                active_interfaces = []

                # 遍历所有网络接口，找到活跃的IPv4接口
                for interface, addrs in net_if_addrs.items():
                    for addr in addrs:
                        # 检查是否为IPv4地址且不是本地回环地址（127.x.x.x）
                        if (hasattr(addr, 'family') and
                                addr.family == 2 and
                                not addr.address.startswith('127.')):
                            active_interfaces.append(interface)
                            break

                # 格式化输出网络速度
                print(f"上传速度: {self.format_speed(upload_speed):>10} | "
                      f"下载速度: {self.format_speed(download_speed):>10} | "
                      f"活跃接口: {', '.join(active_interfaces[:2])}")

                # 记录网络速度到日志文件
                self.logger.info(
                    f"网络速度 - 上传: {self.format_speed(upload_speed)}, 下载: {self.format_speed(download_speed)}")

                # 检查网络速度是否超过警告阈值
                if upload_speed > self.config['network_speed_warning'] or download_speed > self.config[
                    'network_speed_warning']:
                    self.logger.warning(
                        f"网络速度异常 - 上传: {self.format_speed(upload_speed)}, 下载: {self.format_speed(download_speed)}")

                # 更新上一次的值，为下次计算做准备
                last_bytes_sent = current_bytes_sent
                last_bytes_recv = current_bytes_recv
                last_time = current_time

                # 按配置的间隔时间休眠
                time.sleep(interval)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("网络速度监控已停止")
            print("\n网络速度监控已停止")
        except Exception as e:
            # 监控过程中出现异常
            self.logger.error(f"网络速度监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def monitor_system_resources(self, interval: float = None) -> None:
        """
        同时监控CPU、内存和磁盘使用情况

        这是一个综合监控方法，同时监控系统的三个主要资源指标：
        CPU使用率、内存使用率和磁盘使用率。这种方法可以快速了解
        系统的整体资源使用情况，适合日常系统监控。

        Args:
            interval (float, optional): 监控间隔时间（秒），如果为None则使用配置文件中的值

        监控内容：
        - CPU使用率（百分比）
        - 内存使用率（百分比）和内存使用量（GB）
        - 磁盘使用率（百分比）和磁盘使用量（GB）
        - 多资源警告阈值检查

        输出格式：
        - 控制台：单行显示所有资源使用情况
        - 日志文件：记录监控数据和警告信息

        注意事项：
        - 磁盘监控可能因权限问题失败，会记录警告但不影响其他监控
        - 所有资源都有独立的警告阈值配置
        """
        # 如果没有指定间隔时间，使用配置文件中的默认值
        if interval is None:
            interval = self.config['monitor_interval']

        # 记录开始监控的日志
        self.logger.info("开始系统资源综合监控")

        try:
            # 显示监控开始信息
            print("开始监控系统资源使用情况")
            print("按 Ctrl+C 停止监控")
            print("=" * 80)  # 分隔线

            # 主监控循环
            while self.monitoring:
                # 获取CPU使用率（指定间隔时间内的平均值）
                cpu_percent = psutil.cpu_percent(interval=interval)

                # 获取内存信息
                memory = psutil.virtual_memory()
                memory_percent = memory.percent  # 内存使用率（百分比）
                total_gb = memory.total / (1024 ** 3)  # 总内存（GB）
                used_gb = memory.used / (1024 ** 3)  # 已使用内存（GB）

                # 获取磁盘使用情况（可能因权限问题失败）
                try:
                    disk = psutil.disk_usage('/')  # 获取根目录磁盘使用情况
                    disk_percent = (disk.used / disk.total) * 100  # 磁盘使用率（百分比）
                    disk_total_gb = disk.total / (1024 ** 3)  # 总磁盘空间（GB）
                    disk_used_gb = disk.used / (1024 ** 3)  # 已使用磁盘空间（GB）
                except Exception as e:
                    # 如果无法获取磁盘信息，记录警告并使用默认值
                    self.logger.warning(f"无法获取磁盘信息: {str(e)}")
                    disk_percent = 0
                    disk_total_gb = 0
                    disk_used_gb = 0

                # 格式化输出所有资源使用情况（单行显示）
                print(f"CPU: {cpu_percent:5.1f}% | "
                      f"内存: {memory_percent:5.1f}% ({used_gb:5.1f}GB/{total_gb:5.1f}GB) | "
                      f"磁盘: {disk_percent:5.1f}% ({disk_used_gb:5.1f}GB/{disk_total_gb:5.1f}GB)")

                # 记录系统资源使用情况到日志文件
                self.logger.info(
                    f"系统资源 - CPU: {cpu_percent:.1f}%, 内存: {memory_percent:.1f}%, 磁盘: {disk_percent:.1f}%")

                # 检查各个资源的警告阈值
                if cpu_percent > self.config['cpu_warning_threshold']:
                    self.logger.warning(f"CPU使用率过高: {cpu_percent:.1f}%")
                if memory_percent > self.config['memory_warning_threshold']:
                    self.logger.warning(f"内存使用率过高: {memory_percent:.1f}%")
                if disk_percent > self.config['disk_warning_threshold']:
                    self.logger.warning(f"磁盘使用率过高: {disk_percent:.1f}%")

                # 按配置的间隔时间休眠
                time.sleep(interval)

        except KeyboardInterrupt:
            # 用户按Ctrl+C停止监控
            self.logger.info("系统资源监控已停止")
            print("\n系统资源监控已停止")
        except Exception as e:
            # 监控过程中出现异常
            self.logger.error(f"系统资源监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def monitor_running_applications(self, interval: float = None, top_n: int = 10) -> None:
        """
        监控当前运行的应用程序
        """
        if interval is None:
            interval = self.config['monitor_interval']

        self.logger.info("开始应用程序监控")

        try:
            print("开始监控运行中的应用程序")
            print("按 Ctrl+C 停止监控")
            print("=" * 80)

            while self.monitoring:
                # 获取所有进程
                processes = []
                for proc in psutil.process_iter(
                        ['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
                    try:
                        proc_info = proc.info
                        if proc_info['cpu_percent'] > 0 or proc_info['memory_percent'] > 0:
                            processes.append(proc_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

                # 按CPU使用率排序
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

                print(f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"总进程数: {len(processes)}")
                print("-" * 80)
                print(f"{'PID':<8} {'进程名':<20} {'CPU%':<8} {'内存%':<8} {'内存(MB)':<12} {'状态':<8}")
                print("-" * 80)

                # 显示前N个进程
                for i, proc in enumerate(processes[:top_n]):
                    try:
                        pid = proc['pid']
                        name = proc['name'][:18] if proc['name'] else 'Unknown'
                        cpu_percent = proc['cpu_percent']
                        memory_percent = proc['memory_percent']
                        memory_mb = proc['memory_info'].rss / (1024 * 1024) if proc['memory_info'] else 0
                        status = proc['status']

                        print(
                            f"{pid:<8} {name:<20} {cpu_percent:<8.1f} {memory_percent:<8.1f} {memory_mb:<12.1f} {status:<8}")

                        # 记录高资源占用进程
                        if cpu_percent > self.config['process_cpu_warning'] or memory_percent > self.config[
                            'process_memory_warning']:
                            self.logger.warning(
                                f"高资源占用进程 - PID: {pid}, 名称: {name}, CPU: {cpu_percent:.1f}%, 内存: {memory_percent:.1f}%")

                    except Exception as e:
                        continue

                # 记录日志
                self.logger.info(f"当前运行进程数: {len(processes)}")

                print("-" * 80)
                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("应用程序监控已停止")
            print("\n应用程序监控已停止")
        except Exception as e:
            self.logger.error(f"应用程序监控出错: {str(e)}")
            print(f"\n监控出错: {str(e)}")

    def get_detailed_process_info(self, pid: Optional[int] = None) -> None:
        """
        获取详细进程信息
        """
        try:
            if pid:
                # 获取指定进程的详细信息
                proc = psutil.Process(pid)
                print(f"\n进程详细信息 - PID: {pid}")
                print("=" * 50)

                # 基本信息
                print(f"进程名: {proc.name()}")
                print(f"状态: {proc.status()}")
                print(f"创建时间: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")

                # CPU信息
                cpu_percent = proc.cpu_percent()
                print(f"CPU使用率: {cpu_percent:.1f}%")

                # 内存信息
                memory_info = proc.memory_info()
                memory_percent = proc.memory_percent()
                print(f"内存使用: {memory_info.rss / (1024 * 1024):.1f} MB ({memory_percent:.1f}%)")

                # 线程信息
                print(f"线程数: {proc.num_threads()}")

                # 网络连接
                try:
                    connections = proc.connections()
                    print(f"网络连接数: {len(connections)}")
                except:
                    print("网络连接数: 无法获取")

                # 打开的文件
                try:
                    open_files = proc.open_files()
                    print(f"打开文件数: {len(open_files)}")
                except:
                    print("打开文件数: 无法获取")

                self.logger.info(f"获取进程 {pid} 的详细信息")

            else:
                # 显示所有进程的简要信息
                print("\n当前运行的所有进程:")
                print("=" * 80)
                print(f"{'PID':<8} {'进程名':<25} {'状态':<10} {'CPU%':<8} {'内存%':<8}")
                print("-" * 80)

                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                    try:
                        proc_info = proc.info
                        processes.append(proc_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

                # 按进程名排序
                processes.sort(key=lambda x: x['name'] or '')

                for proc in processes:
                    pid = proc['pid']
                    name = (proc['name'] or 'Unknown')[:23]
                    status = proc['status']
                    cpu_percent = proc['cpu_percent']
                    memory_percent = proc['memory_percent']

                    print(f"{pid:<8} {name:<25} {status:<10} {cpu_percent:<8.1f} {memory_percent:<8.1f}")

                self.logger.info(f"获取了 {len(processes)} 个进程的简要信息")

        except psutil.NoSuchProcess:
            print(f"进程 {pid} 不存在")
            self.logger.error(f"进程 {pid} 不存在")
        except psutil.AccessDenied:
            print(f"无法访问进程 {pid} 的信息（权限不足）")
            self.logger.error(f"无法访问进程 {pid} 的信息（权限不足）")
        except Exception as e:
            print(f"获取进程信息时出错: {str(e)}")
            self.logger.error(f"获取进程信息时出错: {str(e)}")

    def start_monitoring(self, monitor_type: str, **kwargs) -> None:
        """
        开始监控

        根据指定的监控类型启动相应的监控功能。这是一个统一的入口方法，
        支持多种监控类型，并可以传递额外的参数。

        Args:
            monitor_type (str): 监控类型，支持以下值：
                - "cpu": CPU使用率监控
                - "memory": 内存使用情况监控
                - "network": 网络速度监控
                - "system": 系统资源综合监控
                - "applications": 应用程序监控
            **kwargs: 传递给具体监控方法的额外参数，如：
                - interval: 监控间隔时间
                - top_n: 显示前N个进程（仅applications类型）

        使用示例：
            monitor.start_monitoring("cpu", interval=2)
            monitor.start_monitoring("system", interval=1)
            monitor.start_monitoring("applications", top_n=20)
        """
        # 设置监控状态为True，表示开始监控
        self.monitoring = True

        # 根据监控类型调用相应的监控方法
        if monitor_type == "cpu":
            # CPU使用率监控
            self.monitor_cpu_usage(**kwargs)
        elif monitor_type == "memory":
            # 内存使用情况监控
            self.monitor_memory_usage(**kwargs)
        elif monitor_type == "network":
            # 网络速度监控
            self.monitor_network_speed(**kwargs)
        elif monitor_type == "system":
            # 系统资源综合监控
            self.monitor_system_resources(**kwargs)
        elif monitor_type == "applications":
            # 应用程序监控
            self.monitor_running_applications(**kwargs)
        else:
            # 未知的监控类型
            print(f"未知的监控类型: {monitor_type}")
            print("支持的监控类型: cpu, memory, network, system, applications")

    def stop_monitoring(self) -> None:
        """
        停止监控

        停止当前正在进行的监控，设置监控状态为False，
        并等待监控线程结束（如果存在）。

        这个方法会：
        1. 设置监控状态标志为False
        2. 等待监控线程结束（如果存在）
        3. 清理相关资源

        注意：这个方法通常由监控方法内部调用（如KeyboardInterrupt），
        也可以手动调用来停止监控。
        """
        # 设置监控状态为False，停止监控循环
        self.monitoring = False

        # 如果存在监控线程且线程还在运行，等待线程结束
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join()
            print("监控已停止")


# =============================================================================
# 向后兼容性函数接口
#
# 这些函数是为了保持与旧版本代码的兼容性而保留的。
# 它们内部使用SystemMonitor类来实现功能，但提供简单的函数接口。
# 建议新代码直接使用SystemMonitor类，以获得更好的功能和性能。
# =============================================================================

def setup_logging():
    """
    配置日志系统（向后兼容）

    这个函数是为了保持与旧版本代码的兼容性而保留的。
    它创建一个SystemMonitor实例并返回其日志记录器。

    Returns:
        logging.Logger: 配置好的日志记录器

    注意：建议新代码直接使用SystemMonitor类，而不是这个函数。
    """
    monitor = SystemMonitor()
    return monitor.logger


def monitor_cpu_usage(interval=1):
    """
    实时监控并打印CPU占用率（向后兼容）

    这个函数是为了保持与旧版本代码的兼容性而保留的。
    它创建一个SystemMonitor实例并启动CPU监控。

    Args:
        interval (int): 监控间隔时间（秒），默认为1秒

    注意：建议新代码直接使用SystemMonitor类，而不是这个函数。
    """
    monitor = SystemMonitor()
    monitor.start_monitoring("cpu", interval=interval)


def monitor_memory_usage(interval=1):
    """
    实时监控并打印内存使用情况（向后兼容）

    这个函数是为了保持与旧版本代码的兼容性而保留的。
    它创建一个SystemMonitor实例并启动内存监控。

    Args:
        interval (int): 监控间隔时间（秒），默认为1秒

    注意：建议新代码直接使用SystemMonitor类，而不是这个函数。
    """
    monitor = SystemMonitor()
    monitor.start_monitoring("memory", interval=interval)


def monitor_network_speed(interval=1):
    """
    实时监控网络速度（向后兼容）

    这个函数是为了保持与旧版本代码的兼容性而保留的。
    它创建一个SystemMonitor实例并启动网络速度监控。

    Args:
        interval (int): 监控间隔时间（秒），默认为1秒

    注意：建议新代码直接使用SystemMonitor类，而不是这个函数。
    """
    monitor = SystemMonitor()
    monitor.start_monitoring("network", interval=interval)


def monitor_system_resources(interval=1):
    """
    同时监控CPU、内存和磁盘使用情况（向后兼容）

    这个函数是为了保持与旧版本代码的兼容性而保留的。
    它创建一个SystemMonitor实例并启动系统资源综合监控。

    Args:
        interval (int): 监控间隔时间（秒），默认为1秒

    注意：建议新代码直接使用SystemMonitor类，而不是这个函数。
    """
    monitor = SystemMonitor()
    monitor.start_monitoring("system", interval=interval)


def monitor_running_applications(interval=5, top_n=10):
    """
    监控当前运行的应用程序（向后兼容）

    这个函数是为了保持与旧版本代码的兼容性而保留的。
    它创建一个SystemMonitor实例并启动应用程序监控。

    Args:
        interval (int): 监控间隔时间（秒），默认为5秒
        top_n (int): 显示前N个占用资源最多的进程，默认为10

    注意：建议新代码直接使用SystemMonitor类，而不是这个函数。
    """
    monitor = SystemMonitor()
    monitor.start_monitoring("applications", interval=interval, top_n=top_n)


def get_detailed_process_info(pid=None):
    """
    获取详细进程信息（向后兼容）

    这个函数是为了保持与旧版本代码的兼容性而保留的。
    它创建一个SystemMonitor实例并获取进程详细信息。

    Args:
        pid (int, optional): 进程ID，如果为None则显示所有进程的简要信息

    注意：建议新代码直接使用SystemMonitor类，而不是这个函数。
    """
    monitor = SystemMonitor()
    monitor.get_detailed_process_info(pid)


if __name__ == "__main__":
    """
    主程序入口

    当直接运行此脚本时，会执行以下步骤：
    1. 检查并安装必要的依赖
    2. 创建SystemMonitor实例
    3. 显示系统基本信息
    4. 提供交互式菜单选择监控模式
    5. 根据用户选择启动相应的监控功能

    使用方法：
        python Tools.py
    """

    # =============================================================================
    # 依赖检查和安装
    # =============================================================================
    try:
        # 尝试导入psutil库
        import psutil
    except ImportError:
        # 如果psutil未安装，自动安装
        print("正在安装必要的依赖库...")
        import sys
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil

        print("依赖库安装完成！")

    # =============================================================================
    # 创建监控器实例
    # =============================================================================
    print("正在初始化系统监控器...")
    monitor = SystemMonitor()
    print("系统监控器初始化完成！")

    # =============================================================================
    # 显示系统基本信息
    # =============================================================================
    print("\n" + "=" * 60)
    print("系统信息概览")
    print("=" * 60)

    system_info = monitor.get_system_info()
    if system_info:
        print(f"CPU核心数: {system_info.get('cpu_count', 'N/A')}")
        print(f"CPU频率: {system_info.get('cpu_freq', 0):.0f} MHz")
        print(f"内存总量: {monitor.format_bytes(system_info.get('memory_total', 0))}")
        print(f"操作系统: {system_info.get('platform', 'N/A')}")
        print(f"Python版本: {system_info.get('python_version', 'N/A')}")
    else:
        print("无法获取系统信息")

    print("-" * 60)

    # =============================================================================
    # 交互式菜单
    # =============================================================================
    print("\n请选择监控模式:")
    print("1. CPU监控 - 监控CPU使用率和每个核心的详细使用率")
    print("2. 内存监控 - 监控内存使用情况和使用率")
    print("3. 系统资源综合监控 - 同时监控CPU、内存和磁盘使用情况")
    print("4. 网络速度监控 - 监控网络上传和下载速度")
    print("5. 应用程序监控 - 监控运行中的进程和资源占用")
    print("6. 获取进程详细信息 - 查看特定进程或所有进程的详细信息")
    print("0. 退出程序")

    # 获取用户选择
    choice = input("\n请输入选择 (0/1/2/3/4/5/6): ").strip()

    # =============================================================================
    # 根据用户选择启动相应的监控功能
    # =============================================================================
    try:
        if choice == "0":
            print("程序已退出")
        elif choice == "1":
            print("启动CPU监控...")
            monitor.start_monitoring("cpu")
        elif choice == "2":
            print("启动内存监控...")
            monitor.start_monitoring("memory")
        elif choice == "3":
            print("启动系统资源综合监控...")
            monitor.start_monitoring("system")
        elif choice == "4":
            print("启动网络速度监控...")
            monitor.start_monitoring("network")
        elif choice == "5":
            print("启动应用程序监控...")
            monitor.start_monitoring("applications")
        elif choice == "6":
            # 获取进程详细信息
            pid_input = input("请输入进程ID（直接回车显示所有进程）: ").strip()
            if pid_input:
                try:
                    pid = int(pid_input)
                    print(f"获取进程 {pid} 的详细信息...")
                    monitor.get_detailed_process_info(pid)
                except ValueError:
                    print("错误：无效的进程ID，请输入数字")
            else:
                print("显示所有进程的简要信息...")
                monitor.get_detailed_process_info()
        else:
            print("无效选择，默认启动CPU监控...")
            monitor.start_monitoring("cpu")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        print("请检查系统权限或配置文件")
