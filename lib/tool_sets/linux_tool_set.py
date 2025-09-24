import json
import subprocess
from pathlib import Path

from src.tool_set import ToolSet


# def cwd() -> str:
#     """获取当前目录。
#     不需要参数。
#     返回值为当前目录。"""
#     return str(Path.cwd().absolute())


# def listDir(path: str) -> str:
#     """列出输入路径下的所有文件夹。
#     参数`path`为输入的路径。
#     返回值是以json列表格式的字符串。"""
#     return json.dumps([str(i) for i in Path(path).iterdir() if i.is_dir()])


# def listFile(path: str) -> str:
#     """列出输入路径下的所有文件。
#     参数`path`为输入的路径。
#     返回值是以json列表格式的字符串。"""
#     return json.dumps([str(i) for i in Path(path).iterdir() if i.is_file()])


def shellExec(cmd: str) -> str:
    """执行任意shell命令，将运行结果直接显示在终端。
    大语言模型仅需要执行而不需要知道执行结果时调用这个函数。
    参数`cmd`为需要执行的shell命令，
    返回值为执行的返回代码或运行取消。"""
    print("是否执行命令:")
    print("\t" + cmd)
    confrim = input("[Y/n]? ")
    if confrim in ("", "y", "Y"):
        sp = subprocess.run(
            cmd,
            text=True,
            shell=True,
        )
        return str(sp.returncode)
    else:
        return "cancelled"


def shellExecRetText(cmd: str) -> str:
    """执行任意shell命令，将输出结果作为返回值返回。
    当大语言模型需要命令执行的结果时调用这个函数。
    命令执行的结果不会显示在终端。
    参数`cmd`为需要执行的shell命令，
    返回值为命令运行的结果。"""
    print("是否执行命令:")
    print("\t" + cmd)
    confrim = input("[Y/n]? ")
    if confrim in ("", "y", "Y"):
        sp = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        return str(sp.stdout)
    else:
        return "用户取消执行该shell命令。"


linux_tool_set = ToolSet([shellExec, shellExecRetText])
