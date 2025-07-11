import concurrent
from contextlib import contextmanager

import requests
import time
from concurrent.futures import ThreadPoolExecutor

from Python核心语法学习指南code.week1.通用日志处理模块.日志配置类 import LoggerFactory

# 获取日志记录器，配置日志文件路径和日志级别
logger = LoggerFactory.get_logger("api_client", {
    "log_file": "logs/api_client.log",
    "level": "DEBUG"
})


class APIClient:
    """
    API客户端类，支持带日志、异常处理、重试、速率限制和并发请求。
    """
    def __init__(self, base_url, max_retries=3, timeout=5):
        """
        初始化APIClient实例。
        参数：
            base_url (str): API基础URL。
            max_retries (int): 请求失败时的最大重试次数。
            timeout (int/float): 每次请求的超时时间（秒）。
        属性：
            session (requests.Session): 复用的HTTP会话对象，自动带上通用请求头。
        """
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "APIClient/1.0",
            "Accept": "application/json"
        })

    @contextmanager
    def rate_limiter(self, max_requests=5, per_second=1):
        """
        API速率限制的上下文管理器。
        参数：
            max_requests (int): 每个时间窗口内允许的最大请求数。
            per_second (float): 时间窗口长度（秒）。
        用法：
            with client.rate_limiter():
                ...
        """
        start_time = time.time()  # 记录窗口起始时间
        request_count = 0         # 当前窗口内的请求计数

        def make_request(endpoint, **kwargs):
            nonlocal request_count

            # 检查速率限制
            elapsed = time.time() - start_time
            if request_count >= max_requests and elapsed < per_second:
                sleep_time = per_second - elapsed
                logger.warning(f"达到速率限制，等待 {sleep_time:.2f}秒")
                time.sleep(sleep_time)

            request_count += 1
            return self._request(endpoint, **kwargs)

        yield make_request  # 作为上下文管理器的返回值

    def _request(self, endpoint, method="GET", params=None, data=None, headers=None):
        """
        执行一次API请求，带重试、日志和异常处理。
        参数：
            endpoint (str): API接口路径（不含base_url）。
            method (str): HTTP方法，如GET、POST等。
            params (dict): 查询参数。
            data (dict): 请求体数据（自动转为JSON）。
            headers (dict): 额外请求头。
        返回值：
            dict: 响应的JSON数据。
        异常：
            请求失败且重试用尽时抛出异常。
        """
        url = f"{self.base_url}/{endpoint}"  # 拼接完整URL
        full_headers = {**self.session.headers, **(headers or {})}  # 合并请求头

        for attempt in range(self.max_retries + 1):  # 支持重试
            try:
                logger.debug(f"请求: {method} {url} (尝试 {attempt + 1})")
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=full_headers,
                    timeout=self.timeout
                )

                response.raise_for_status()  # 检查HTTP状态码，非2xx抛异常
                logger.debug(f"成功: {method} {url} - 状态码 {response.status_code}")
                return response.json()  # 返回JSON数据

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    sleep_time = 2 ** attempt  # 指数退避，逐次延长等待时间
                    logger.warning(f"请求失败: {e}, {attempt + 1}/{self.max_retries}次重试, 等待 {sleep_time}秒")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"请求失败: {method} {url} - {e}")
                    raise  # 重试用尽后抛出异常

    def get_users(self, user_ids):
        """
        并发获取多个用户信息。
        参数：
            user_ids (list): 用户ID列表。
        返回值：
            dict: 用户ID到用户信息的映射，失败时为{"error": ...}。
        说明：
            使用线程池并发请求，自动处理异常和日志。
        """
        with ThreadPoolExecutor() as executor, self.rate_limiter():
            # 提交所有用户请求到线程池
            futures = {
                executor.submit(self._request, f"users/{user_id}"): user_id
                for user_id in user_ids
            }

            results = {}
            # as_completed会在每个future完成时返回
            for future in concurrent.futures.as_completed(futures):
                user_id = futures[future]
                try:
                    results[user_id] = future.result()  # 获取请求结果
                except Exception as e:
                    logger.exception(f"获取用户 {user_id} 失败")
                    results[user_id] = {"error": str(e)}  # 记录错误信息

            return results


# 使用示例
if __name__ == "__main__":
    client = APIClient("https://api.example.com")  # 创建API客户端实例

    # 单请求示例
    try:
        user_data = client._request("users/123")  # 获取单个用户信息
        logger.info(f"用户数据: {user_data}")
    except Exception:
        logger.error("无法获取用户数据")

    # 并发请求示例
    try:
        users = client.get_users([123, 456, 789, 101])  # 并发获取多个用户
        logger.info(f"获取的用户: {list(users.keys())}")
    except Exception:
        logger.error("批量获取用户失败")