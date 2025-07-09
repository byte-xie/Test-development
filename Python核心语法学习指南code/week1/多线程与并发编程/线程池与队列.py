import threading
import time
from concurrent.futures import ThreadPoolExecutor
import queue
import random


def process_task(task_id):
    """
    模拟任务处理函数。
    参数：
        task_id (int): 任务编号。
    返回值：
        str: 任务完成的描述信息。
    说明：
        随机等待一段时间，模拟任务处理过程。
    """
    processing_time = random.uniform(0.1, 1.0)  # 随机生成0.1~1.0秒的处理时间
    time.sleep(processing_time)  # 模拟任务处理
    result = f"任务 {task_id} 完成 (耗时 {processing_time:.2f}秒)"
    return result


def producer(task_queue, num_tasks):
    """
    生产者线程函数，负责向任务队列中添加任务。
    参数：
        task_queue (queue.Queue): 任务队列，用于存放待处理的任务编号。
        num_tasks (int): 要生产的任务数量。
    返回值：
        无
    说明：
        依次将任务编号放入队列，最后为每个消费者线程放入一个None作为结束信号。
    """
    for i in range(num_tasks):
        task_queue.put(i)  # 将任务编号放入队列
        print(f"已添加任务 {i}")
    # 添加结束信号（None），每个消费者线程一个
    for _ in range(4):  # 4个工作线程
        task_queue.put(None)


def consumer(task_queue, results):
    """
    消费者线程函数，从任务队列中取出任务并处理。
    参数：
        task_queue (queue.Queue): 任务队列。
        results (list): 用于保存每个任务处理结果的列表。
    返回值：
        无
    说明：
        循环从队列取任务，遇到None时退出。处理任务后将结果保存到results列表。
    """
    while True:
        task_id = task_queue.get()  # 从队列取出一个任务
        if task_id is None:  # None为结束信号
            break
        result = process_task(task_id)  # 处理任务
        results.append(result)  # 保存结果
        task_queue.task_done()  # 通知队列该任务已完成


# 创建任务队列和结果列表
task_queue = queue.Queue()  # 线程安全的队列，用于存放任务
results = []  # 用于保存所有任务的处理结果

# 创建生产者线程
producer_thread = threading.Thread(
    target=producer,  # 目标函数
    args=(task_queue, 20)  # 参数：任务队列和任务数量
)

# 创建线程池并启动消费者线程
with ThreadPoolExecutor(max_workers=4) as executor:
    # 启动生产者线程，开始向队列中添加任务
    producer_thread.start()

    # 提交4个消费者任务到线程池，每个线程负责不断从队列取任务
    futures = [
        executor.submit(consumer, task_queue, results)
        for _ in range(4)
    ]

    # 等待生产者线程结束（即所有任务都已放入队列）
    producer_thread.join()

    # 等待队列中的所有任务都被处理完（即task_done被调用足够多次）
    task_queue.join()

# 输出所有任务的处理结果
print("\n所有任务完成结果:")
for result in results:
    print(result)