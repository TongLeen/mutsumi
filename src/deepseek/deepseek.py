from collections.abc import Generator
from typing import TYPE_CHECKING, Literal, overload, NamedTuple, Any

import readline
from openai import OpenAI

from .context import Context, Response

if TYPE_CHECKING:
    from openai.resources.chat import Completions


class DeepSeek:
    def __init__(self, key: str) -> None:
        self.key = key
        self.ai = OpenAI(
            api_key=key,
            base_url="https://api.deepseek.com",
        ).chat.completions
        return

    def create(self, system_prompt: str | None = None) -> "Context":
        return Context(self.ai, system_prompt)

    def interact(self, ctx: Context) -> None:

        while True:
            try:
                l = input("> ")
            except KeyboardInterrupt:
                print("")
                return
            r = ctx.ask(l, mode="reasoner")

            if k := r.reasoning_content:
                print("思考过程:")
                print(k)

            print("回答:")
            print(r.content)
