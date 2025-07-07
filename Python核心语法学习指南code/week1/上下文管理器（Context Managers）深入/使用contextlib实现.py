from contextlib import contextmanager
import time


@contextmanager
def performance_time(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"{label} 耗时: {end - start:.6f}秒")


with performance_time("大型计算任务"):
    total = 0
    for i in range(100000000):
        total += i
    print(f"计算结果：{total}")
