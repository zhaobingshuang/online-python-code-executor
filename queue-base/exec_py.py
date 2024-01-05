import json
import sys


input_queue = []


class InputRequestException(Exception):
    """
    抛出此异常表示需要用户输入
    """
    pass


def execute(param):
    # 重写 input 函数
    __builtins__.input = input_wrapper

    # input_queue
    global input_queue
    input_queue = param["input_queue"]
    try:
        # 执行代码
        exec(param["code"])
    except InputRequestException as e:
        # 如果需要用户输入，则直接退出
        sys.stdout.write("\n" + "InputRequestException" + e.args[0])
        exit()


def input_wrapper(prompt=''):
    # 从 input_queue 中弹出
    if input_queue:
        input_str = input_queue.pop(0)
        sys.stdout.write(str(prompt) + input_str + "\n")
        return input_str
    # 需要用户输入
    raise InputRequestException(str(prompt))


if __name__ == '__main__':
    # 从标准输入读取 json 参数：code、input_queue
    arg = sys.stdin.read()
    # 执行
    execute(json.loads(arg))
