from contextlib import contextmanager


class Transaction:
    def __init__(self):
        self.actions = []

    def add_action(self, action):
        self.actions.append(action)

    def commit(self):
        print("提交事务")
        for action in self.actions:
            print(f"执行: {action}")

    def rollback(self):
        print("回滚事务")
        self.actions.clear()


@contextmanager
def transaction_manager():
    tx = Transaction()
    try:
        yield tx
        tx.commit()
    except Exception as e:
        print(f"事务出错: {e}")
        tx.rollback()
        raise


# 使用示例
try:
    with transaction_manager() as tx:
        tx.add_action("创建用户")
        tx.add_action("更新账户")
        tx.add_action("记录日志")
        # 模拟错误
        # raise ValueError("数据库连接失败")
except Exception:
    print("事务处理失败")