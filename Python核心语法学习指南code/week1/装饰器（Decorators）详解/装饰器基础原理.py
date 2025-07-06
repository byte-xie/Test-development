def basic_decorator(func):
    """"
    装饰器基础原理
    """

    def wrapper():
        print("函数执行前操作")
        func()
        print("函数执行后操作")

    return wrapper


def param_decorator(func):
    """
    处理带参数的函数
    """

    def wrapper(*args, **kwargs):
        print(f"调用函数：{func.__name__}")
        print(f"参数: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"返回值：{result}")
        return result

    return wrapper


def repeat(num_times):
    """
    带参数的装饰器
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(num_times):
                print(f"执行{i + 1} 次")
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


class TimerDecorator:
    """
    装饰器堆叠与顺序
    """

    def __init__(self, func):
        self.func = func
        self.times = []

    def __call__(self, *args, **kwargs):
        import time
        start = time.perf_counter()
        result = self.func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        self.times.append(elapsed)

        print(f"{self.func.__name__} 执行时间: {elapsed:.6f}秒")
        print(f"平均执行时间: {sum(self.times) / len(self.times):.6f}秒")
        return result


"""
装饰器堆叠与顺序
"""


def decorator1(func):
    def wrapper():
        print("装饰器1 - 前")
        func()
        print("装饰器1 - 后")

    return wrapper


def decorator2(func):
    def wrapper():
        print("装饰器2 - 前")
        func()
        print("装饰器2 - 后")

    return wrapper


@basic_decorator
def greet():
    print("hello world")


@param_decorator
def add(a, b, c):
    return a + b + c


@repeat(num_times=3)
def say_hello(name):
    print(f"hello, {name}")


@TimerDecorator
def calculate_sum(n):
    return sum(range(n))


@decorator1
@decorator2
def my_function():
    print("原始函数")


if __name__ == '__main__':
    # greet()
    # print(add(3, 5, 5))
    # say_hello("hello world")
    # calculate_sum(1000000000)
    my_function()