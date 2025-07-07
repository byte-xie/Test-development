class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        print(f"连接数据库: {self.db_name}")
        # 模拟数据库连接
        self.connection = {"status": "connected", "db": self.db_name}
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"关闭数据库连接: {self.db_name}")
        # 模拟关闭连接
        self.connection["status"] = "disconnected"

        # 处理异常
        if exc_type is not None:
            print(f"发生异常: {exc_type.__name__}: {exc_value}")
            # 返回True表示异常已处理，不再传播
            return True


# 使用示例
with DatabaseConnection("my_database") as db:
    print(f"当前状态: {db['status']}")
    # 模拟操作
    db["query"] = "SELECT * FROM users"
    # 如果发生异常
    # raise ValueError("模拟数据库错误")

print(f"连接后状态: {db['status']}")