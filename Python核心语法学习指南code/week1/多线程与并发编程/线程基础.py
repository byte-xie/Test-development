import threading
import time


def worker(task_id, delay):
    """
    工作线程函数，模拟一个耗时任务。
    参数：
        task_id (int): 任务编号，用于区分不同线程。
        delay (float): 任务执行的延迟时间（秒），模拟任务耗时。
    返回值：
        无
    说明：
        打印任务开始和结束信息，并休眠delay秒模拟任务处理。
    """
    print(f"任务 {task_id} 开始")
    time.sleep(delay)  # 模拟任务耗时
    print(f"任务 {task_id} 完成 (耗时 {delay}秒)")


# 创建并启动线程
threads = []  # 用于保存所有线程对象的列表
for i in range(1, 6):  # 循环5次，创建5个线程
    # 创建线程对象
    # target: 线程要执行的目标函数
    # args: 传递给目标函数的参数（以元组形式）
    t = threading.Thread(target=worker, args=(i, i * 0.5))
    t.start()  # 启动线程，线程开始执行worker函数
    threads.append(t)  # 将线程对象保存到列表，便于后续管理

# 等待所有线程完成
for t in threads:
    t.join()  # 主线程阻塞，直到每个子线程执行完毕

# print(threads)  # 可选：打印所有线程对象
print("所有任务完成")  # 所有线程结束后输出
