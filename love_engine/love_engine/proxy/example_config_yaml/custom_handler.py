import time
from typing import Any, Optional

import love_engine
from love_engine import CustomLLM, ImageObject, ImageResponse, completion, get_llm_provider
from love_engine.llms.custom_httpx.http_handler import AsyncHTTPHandler
from love_engine.types.utils import ModelResponse


class MyCustomLLM(CustomLLM):
    def completion(self, *args, **kwargs) -> ModelResponse:
        return love_engine.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello world"}],
            mock_response="Hi!",
        )  # type: ignore

    async def acompletion(self, *args, **kwargs) -> love_engine.ModelResponse:
        return love_engine.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello world"}],
            mock_response="Hi!",
        )  # type: ignore


my_custom_llm = MyCustomLLM()
