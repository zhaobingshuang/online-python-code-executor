import json
import os
import subprocess
import threading
from threading import Timer

import psutil


class AbstractExecutor:

    def __init__(self, param):
        # param 包括 code、input_queue
        self.param = param
        # 用于保护 is_timeout 的锁
        self.lock = threading.Lock()
        # 是否执行超时了
        self.is_timeout = None

    def timeout_callback(self, p: subprocess.Popen):
        """
        执行超时时的回调，会终止执行 python 代码的进程组
        :param p: 执行 python 代码的进程
        """
        with self.lock:
            if self.is_timeout is None:
                self.is_timeout = True

        if self.is_timeout:
            try:
                # 终止执行 python 代码的进程组
                self.terminating_process_group(p)
            except Exception as e:
                print("超时回调异常, error: %s", e)

    def terminating_process_group(self, p: subprocess.Popen):
        """
        终止进程 p 及其子进程
        :param p: 要终止的进程
        """
        raise NotImplementedError()

    def create_popen(self) -> subprocess.Popen:
        """
        创建 subprocess.Popen，必须将 stderr 重定向到 stdout
        """
        raise NotImplementedError()

    def output(self, stdout):
        if stdout is not None:
            return stdout.decode("utf-8")
        else:
            return ""

    def execute(self):
        p = self.create_popen()
        timer = Timer(3, self.timeout_callback, [p])
        timer.start()
        try:
            # 从标准输入传入 json 参数：code、input_queue
            p.stdin.write(json.dumps(self.param).encode(encoding="utf-8"))

            stdout, stderr = p.communicate()

            with self.lock:
                if self.is_timeout is None:
                    self.is_timeout = False

        finally:
            timer.cancel()
        return self.is_timeout, self.output(stdout)


class WindowsExecutor(AbstractExecutor):

    __output_prefix = "Active code page: 65001\r\n"

    def create_popen(self) -> subprocess.Popen:
        filename = r"D:\project\python\online-python-code-executor\queue-base\exec_py.py"
        cmd = 'chcp 65001 & set PYTHONIOENCODING=utf-8 & python ' + filename

        # 将 stderr 重定向到了 stdout
        return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=True)

    def terminating_process_group(self, p: subprocess.Popen):
        proc_pid = p.pid
        parent_proc = psutil.Process(proc_pid)
        for child_proc in parent_proc.children(recursive=True):
            print(child_proc.pid)
            child_proc.kill()
        parent_proc.kill()
        print(parent_proc.pid)

    def output(self, stdout):
        output = super().output(stdout)
        if output.startswith(self.__output_prefix):
            return output.removeprefix(self.__output_prefix)
        else:
            return output


if os.name == "nt":
    executor_cls = WindowsExecutor


def execute(param):

    # 执行用户代码
    is_timeout, stdout = executor_cls(param).execute()

    if is_timeout:
        # 执行超时了
        return {
            "is_timeout": is_timeout,
            "done": True,
            "output": stdout,
        }
    else:
        arr = stdout.split("InputRequestException")
        if len(arr) > 1:
            # 需要用户输入
            return {
                "is_timeout": is_timeout,
                "done": False,
                "event": {
                    "type": "input_request",
                    "prompt": arr[-1]
                }
            }
        else:
            # 正常执行结束
            return {
                "is_timeout": is_timeout,
                "done": True,
                "output": stdout,
            }
