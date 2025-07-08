import threading
import time


def worker(task_id, delay):
    print(f"任务 {task_id} 开始")
    time.sleep(delay)
    print(f"任务 {task_id} 完成 (耗时 {delay}秒)")


# 创建并启动线程
threads = []
for i in range(1, 6):
    t = threading.Thread(target=worker, args=(i, i * 0.5))
    t.start()
    threads.append(t)

# 等待所有线程完成
for t in threads:
    t.join()
print(threads)
print("所有任务完成")
