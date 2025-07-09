import threading
import time

# 银行账户类，演示线程安全的存取款操作
class BankAccount:
    def __init__(self):
        self.balance = 1000  # 账户余额，初始为1000元
        self.lock = threading.Lock()  # 创建一个互斥锁对象，用于保证多线程操作时的同步

    def deposit(self, amount):
        """
        存款方法，向账户余额增加指定金额。
        参数：
            amount (int/float): 要存入的金额。
        返回值：
            无
        说明：
            使用with语句自动加锁和释放锁，保证同一时刻只有一个线程能修改余额，防止数据竞争。
        """
        with self.lock:  # 加锁，进入临界区
            print(f"存款 {amount}, 当前余额: {self.balance}")
            new_balance = self.balance + amount  # 计算新余额
            time.sleep(0.1)  # 模拟存款处理时间，便于观察并发问题
            self.balance = new_balance  # 更新余额
            # 释放锁（with语句块结束自动释放）

    def withdraw(self, amount):
        """
        取款方法，从账户余额扣除指定金额。
        参数：
            amount (int/float): 要取出的金额。
        返回值：
            实际取出的金额（int/float），如果余额不足则返回0。
        说明：
            取款操作也需要加锁，保证余额检查和扣减的原子性，防止并发下出现超取。
        """
        with self.lock:  # 加锁，进入临界区
            if self.balance >= amount:
                print(f"取款 {amount}, 当前余额: {self.balance}")
                new_balance = self.balance - amount  # 计算新余额
                time.sleep(0.1)  # 模拟取款处理时间
                self.balance = new_balance  # 更新余额
                return amount  # 返回实际取出金额
            else:
                print(f"取款失败 {amount}, 余额不足")
                return 0  # 余额不足，返回0

# 账户操作函数，依次执行一组存取款操作
def account_user(account, operations):
    """
    模拟一个用户对同一个账户进行一系列存取款操作。
    参数：
        account (BankAccount): 要操作的银行账户对象。
        operations (list): 操作列表，正数表示存款，负数表示取款。
    返回值：
        无
    说明：
        依次遍历操作列表，根据正负分别调用存款或取款方法。
    """
    for op in operations:
        if op > 0:
            account.deposit(op)  # 正数为存款
        else:
            account.withdraw(-op)  # 负数为取款，取绝对值

# 创建一个银行账户实例，初始余额1000元
account = BankAccount()
# 定义两组操作，分别由两个线程模拟两个用户同时操作同一个账户
operations1 = [200, -300, 500, -1000]  # 第一个用户的操作序列：存200，取300，存500，取1000
operations2 = [100, -200, 300, -400]   # 第二个用户的操作序列：存100，取200，存300，取400

# 创建两个线程对象，分别执行account_user函数
# 参数说明：
#   target：线程要执行的目标函数
#   args：传递给目标函数的参数（以元组形式）
t1 = threading.Thread(target=account_user, args=(account, operations1))  # 线程1，执行operations1

t2 = threading.Thread(target=account_user, args=(account, operations2))  # 线程2，执行operations2

# 启动两个线程，开始并发执行
# 线程启动后会异步执行account_user函数
# 由于两个线程共享同一个BankAccount对象，必须依靠锁保证数据安全
t1.start()
t2.start()

# 主线程等待两个子线程执行完毕（即所有操作完成）
t1.join()
t2.join()

# 输出最终余额，验证多线程下数据是否正确
print(f"最终余额: {account.balance}")
