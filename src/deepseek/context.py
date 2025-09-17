from typing import TYPE_CHECKING, Literal, Any

from openai import NotGiven, NOT_GIVEN
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionMessageFunctionToolCall,
)
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
from pydantic import BaseModel
from rich import print

if TYPE_CHECKING:
    from .deepseek import Completions


__all__ = ["Context", "Response"]


class Context:
    def __init__(self, ai: "Completions", system_prompt: str | None = None) -> None:
        self.ai = ai
        self.records: list[ChatCompletionMessageParam] = [
            {"content": i, "role": "system"} for i in (system_prompt,) if i
        ]
        return

    def ask(
        self,
        msg: str,
        mode: Literal["chat", "reasoner"] = "chat",
        tool_set: list | NotGiven = NOT_GIVEN,
    ):
        self.records.append({"role": "user", "content": msg})

        raw_rsp = self.ai.create(
            messages=self.records,
            model="deepseek-" + mode,
            tools=tool_set,
            stream=False,
        )
        finish_reason = raw_rsp.choices[0].finish_reason
        rmsg = raw_rsp.choices[0].message

        rsp = Response.parseRawResponse(rmsg)
        self.records.append(rsp.toParam())  # type:ignore

        return finish_reason, rsp

    def sendToolCallRetvals(
        self,
        values: list[tuple[str, Any]],
        mode: Literal["chat", "reasoner"] = "chat",
        tool_set: list | NotGiven = NOT_GIVEN,
    ):
        for v in values:
            self.records.append(
                {
                    "role": "tool",
                    "tool_call_id": v[0],
                    "content": v[1],
                }
            )

        raw_rsp = self.ai.create(
            messages=self.records,
            model="deepseek-" + mode,
            tools=tool_set,
            stream=False,
        )
        finish_reason = raw_rsp.choices[0].finish_reason

        rsp = Response.parseRawResponse(raw_rsp.choices[0].message)
        self.records.append(rsp.toParam())  # type:ignore
        return finish_reason, rsp

    # def askStream(
    #     self,
    #     msg: str,
    #     mode: Literal["chat", "reasoner"] = "chat",
    #     tool_set: dict | NotGiven = NOT_GIVEN,
    # ):
    #     self.records.append({"role": "user", "content": msg})
    #     rsp = self.ai.create(
    #         messages=self.records,
    #         model="deepseek-" + mode,
    #         tools=tool_set,
    #         stream=True,
    #     )

    #     content_buf: list[str] = []
    #     tool_calls_buf: list[ChatCompletionMessageFunctionToolCall] = []
    #     tool_call_buf = ChatCompletionMessageFunctionToolCall()
    #     for c in rsp:
    #         d = c.choices[0].delta
    #         assert not (
    #             d.content
    #             and d.tool_calls
    #             and d.model_extra
    #             and d.model_extra["reasoning_content"]
    #         )
    #         if d.content:
    #             content_buf.append(d.content)
    #             yield "content", d.content
    #         elif d.tool_calls:
    #             yield "tool_calls", (
    #                 ToolCall(
    #                     id=i.id,
    #                     name=i.function.name,
    #                     arguments=i.function.arguments,
    #                 )
    #                 for i in d.tool_calls
    #             )
    #         elif d.model_extra and d.model_extra["reasoning_content"]:
    #             yield "reasoning_content", d.model_extra["reasoning_content"]

    #         yield

    #     self.records.append(
    #         {
    #             "role": "assistant",
    #             "content": "".join(content_buf),
    #             "tool_calls": (
    #                 [
    #                     {
    #                         "id": i.id,
    #                         "type": "function",
    #                         "function": {
    #                             "name": i.function.name,
    #                             "arguments": i.function.arguments,
    #                         },
    #                     }
    #                     for i in tool_calls_buf
    #                     if isinstance(i, ChatCompletionMessageFunctionToolCall)
    #                 ]
    #             ),
    #         }
    #     )
    #     return


class Response(BaseModel):
    content: str | None
    reasoning_content: str | None
    tool_calls: list["ToolCall"]

    @classmethod
    def parseRawResponse(cls, rmsg: ChatCompletionMessage):

        if rmsg.model_extra is None or (
            "reasoning_content" not in rmsg.model_extra.keys()
        ):
            reasoning_content = None
        else:
            reasoning_content = rmsg.model_extra["reasoning_content"]
            assert isinstance(reasoning_content, str) or reasoning_content is None

        if rmsg.tool_calls is None:
            tool_calls = []
        else:
            tool_calls: list[ToolCall] = []
            for f in rmsg.tool_calls:
                if not isinstance(f, ChatCompletionMessageFunctionToolCall):
                    raise TypeError(
                        f"type '{"ChatCompletionMessageFunctionToolCall"}' expected, {type(f)} gotten."
                    )
                id = f.id
                func_name = f.function.name
                func_argu = f.function.arguments
                tool_calls.append(
                    ToolCall(
                        id=id,
                        name=func_name,
                        arguments=func_argu,
                    )
                )
        return cls(
            content=rmsg.content,
            reasoning_content=reasoning_content,
            tool_calls=tool_calls,
        )

    def toParam(self):
        return {
            "role": "assistant",
            "content": self.content,
            "tool_calls": (
                None
                if not self.tool_calls
                else [
                    {
                        "id": i.id,
                        "type": "function",
                        "function": {
                            "name": i.name,
                            "arguments": i.arguments,
                        },
                    }
                    for i in self.tool_calls
                ]
            ),
        }


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str
