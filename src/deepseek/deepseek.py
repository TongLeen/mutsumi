import json
from typing import TYPE_CHECKING, overload

from openai import OpenAI
from rich import print

from ..toolsets import ToolSet

from .context import Context, ContextWithTools
from .logger import DeepSeekLogger, dummy_logger

if TYPE_CHECKING:
    from openai.resources.chat import Completions


__all__ = ["DeepSeek"]


class DeepSeek:
    def __init__(self, key: str) -> None:
        self.key = key
        self.ai = OpenAI(
            api_key=key,
            base_url="https://api.deepseek.com",
        ).chat.completions
        return

    @overload
    def create(
        self,
        *,
        system_prompt: str | None = None,
        log_name: str | None = None,
    ) -> Context: ...

    @overload
    def create(
        self,
        tool_set: ToolSet,
        *,
        system_prompt: str | None = None,
        log_name: str | None = None,
    ) -> ContextWithTools: ...

    def create(
        self,
        tool_set: ToolSet | None = None,
        *,
        system_prompt: str | None = None,
        log_name: str | None = None,
    ):
        logger = DeepSeekLogger(log_name) if log_name is not None else dummy_logger
        if tool_set is None:
            return Context(self.ai, logger, system_prompt)
        else:
            return ContextWithTools(self.ai, logger, tool_set, system_prompt)

    def interact(self, ctx: Context | ContextWithTools) -> None:
        finish_reason = "stop"
        while True:
            if finish_reason == "stop":
                try:
                    s = input("> ")
                except KeyboardInterrupt:
                    exit()

                finish_reason, rsp = ctx.ask(s)

            if isinstance(ctx, ContextWithTools) and (k := rsp.tool_calls):
                retvals: list[tuple[str, str]] = []
                for f in k:
                    fbody = ctx.tool_set.getToolByName(f.name)
                    argus = json.loads(f.arguments)
                    if fbody is None:
                        raise RuntimeError(f"Tool '{f.name}' does not exist.")
                    retval = fbody(**argus)
                    retvals.append((f.id, retval))

            if finish_reason == "stop":
                continue
            elif finish_reason == "tool_calls":
                assert isinstance(ctx, ContextWithTools)
                finish_reason, rsp = ctx.sendToolCallRetvals(retvals)
            else:
                raise RuntimeError(f"Unexpected finish: {finish_reason}")
