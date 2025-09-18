import json

import readline
from rich import print

from src.deepseek import DeepSeek
from src.toolsets import ToolSet

NumberBook = {
    "1": "张三",
    "2": "李四",
    "3": "王五",
}


def getName(id: str) -> str:
    """根据 id 号从本地数据库获取人员的姓名。
    参数 `id` 为人员的识别代码，类型为字符串。
    返回值类型为字符串，为人员的姓名，如果不存在则返回空字符串。"""
    return NumberBook.get(id, "")


test_tool_set = ToolSet([getName])


if __name__ == "__main__":
    with open("cfg/key") as f:
        key = f.read()

    client = DeepSeek(key)
    ctx = client.create(tool_set=test_tool_set)

    try:
        s = input("> ")
    except KeyboardInterrupt:
        exit()

    finish_reason, rsp = ctx.ask(s)

    while True:
        print(rsp)
        if k := rsp.content:
            print(k)

        if k := rsp.tool_calls:
            print(k)
            retvals = []
            for f in k:
                fbody = test_tool_set.getToolByName(f.name)
                if fbody is None:
                    raise RuntimeError(f"No tool named '{f.name}'. Called by deepseek.")
                args = json.loads(f.arguments)
                retval = fbody(**args)
                retvals.append((f.id, retval))

        if finish_reason == "stop":
            try:
                s = input("> ")
            except KeyboardInterrupt:
                exit()

            finish_reason, rsp = ctx.ask(s)
        elif finish_reason == "tool_calls":
            finish_reason, rsp = ctx.sendToolCallRetvals(retvals)
