import threading
import time
from concurrent.futures import ThreadPoolExecutor
import queue
import random


def process_task(task_id):
    """模拟任务处理"""
    processing_time = random.uniform(0.1, 1.0)
    time.sleep(processing_time)
    result = f"任务 {task_id} 完成 (耗时 {processing_time:.2f}秒)"
    return result


def producer(task_queue, num_tasks):
    """生产任务"""
    for i in range(num_tasks):
        task_queue.put(i)
        print(f"已添加任务 {i}")
    # 添加结束信号
    for _ in range(4):  # 4个工作线程
        task_queue.put(None)


def consumer(task_queue, results):
    """消费任务"""
    while True:
        task_id = task_queue.get()
        if task_id is None:
            break
        result = process_task(task_id)
        results.append(result)
        task_queue.task_done()


# 创建任务队列和结果列表
task_queue = queue.Queue()
results = []

# 创建生产者线程
producer_thread = threading.Thread(
    target=producer,
    args=(task_queue, 20)
)

# 创建线程池
with ThreadPoolExecutor(max_workers=4) as executor:
    # 启动生产者
    producer_thread.start()

    # 提交消费者任务
    futures = [
        executor.submit(consumer, task_queue, results)
        for _ in range(4)
    ]

    # 等待生产者完成
    producer_thread.join()

    # 等待所有任务完成
    task_queue.join()

print("\n所有任务完成结果:")
for result in results:
    print(result)