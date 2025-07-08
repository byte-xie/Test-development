class NetworkError(Exception):
    """网络相关异常基类"""


class ConnectionTimeout(NetworkError):
    """连接超时异常"""


class ServerError(NetworkError):
    """服务器错误异常"""


def connect_to_server():
    import random
    # 模拟不同错误
    error_type = random.choice([0, 1, 2, 3])
    if error_type == 0:
        raise ConnectionTimeout("连接超时: 服务器未响应")
    elif error_type == 1:
        raise ServerError("服务器错误: 500 Internal Server Error")
    elif error_type == 2:
        raise ValueError("无效的服务器地址")
    else:
        print("连接成功")


# 异常处理
for attempt in range(1, 4):
    try:
        print(f"\n尝试 #{attempt}")
        connect_to_server()
        break
    except ConnectionTimeout as e:
        print(f"连接超时: {e}")
        print("重试中...")
    except ServerError as e:
        print(f"服务器错误: {e}")
        print("联系管理员...")
        break
    except Exception as e:
        print(f"未预期错误: {type(e).__name__}: {e}")
        break