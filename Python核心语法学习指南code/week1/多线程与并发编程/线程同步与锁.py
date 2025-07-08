import threading
import time


class BankAccount:
    def __init__(self):
        self.balance = 1000
        self.lock = threading.Lock()

    def deposit(self, amount):
        with self.lock:
            print(f"存款 {amount}, 当前余额: {self.balance}")
            new_balance = self.balance + amount
            time.sleep(0.1)  # 模拟处理时间
            self.balance = new_balance

    def withdraw(self, amount):
        with self.lock:
            if self.balance >= amount:
                print(f"取款 {amount}, 当前余额: {self.balance}")
                new_balance = self.balance - amount
                time.sleep(0.1)  # 模拟处理时间
                self.balance = new_balance
                return amount
            else:
                print(f"取款失败 {amount}, 余额不足")
                return 0


def account_user(account, operations):
    for op in operations:
        if op > 0:
            account.deposit(op)
        else:
            account.withdraw(-op)


account = BankAccount()
operations1 = [200, -300, 500, -1000]
operations2 = [100, -200, 300, -400]

t1 = threading.Thread(target=account_user, args=(account, operations1))
t2 = threading.Thread(target=account_user, args=(account, operations2))

t1.start()
t2.start()
t1.join()
t2.join()

print(f"最终余额: {account.balance}")
