def process_data():
    try:
        # 模拟数据处理
        data = {"value": "abc"}
        result = int(data["value"])
        return result
    except Exception as e:
        raise RuntimeError("数据处理失败") from e


try:
    process_data()
except RuntimeError as e:
    print(f"捕获异常: {e}")
    print(f"原始异常: {e.__cause__}")
