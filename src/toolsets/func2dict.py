from collections.abc import Callable

from openai.types.chat import ChatCompletionFunctionToolParam


def pf(f: Callable) -> ChatCompletionFunctionToolParam:
    assert f.__doc__
    return {
        "type": "function",
        "function": {
            "name": f.__name__,
            "description": f.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    k: {
                        "type": "object",
                    }
                    for k in f.__annotations__.keys()
                    if k != "return"
                },
                "required": [i for i in f.__annotations__.keys() if i != "return"],
            },
        },
    }
