"""
Handler for transforming /chat/completions api requests to love_engine.responses requests
"""

from typing import TYPE_CHECKING, Optional, Union

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from love_engine import LoveEngineLoggingObj
    from love_engine.types.llms.openai import HttpxBinaryResponseContent


class SpeechToCompletionBridgeHandlerInputKwargs(TypedDict):
    model: str
    input: str
    voice: Optional[Union[str, dict]]
    optional_params: dict
    love_engine_params: dict
    logging_obj: "LoveEngineLoggingObj"
    headers: dict
    custom_llm_provider: str


class SpeechToCompletionBridgeHandler:
    def __init__(self):
        from .transformation import SpeechToCompletionBridgeTransformationHandler

        super().__init__()
        self.transformation_handler = SpeechToCompletionBridgeTransformationHandler()

    def validate_input_kwargs(
        self, kwargs: dict
    ) -> SpeechToCompletionBridgeHandlerInputKwargs:
        from love_engine import LoveEngineLoggingObj

        model = kwargs.get("model")
        if model is None or not isinstance(model, str):
            raise ValueError("model is required")

        custom_llm_provider = kwargs.get("custom_llm_provider")
        if custom_llm_provider is None or not isinstance(custom_llm_provider, str):
            raise ValueError("custom_llm_provider is required")

        input = kwargs.get("input")
        if input is None or not isinstance(input, str):
            raise ValueError("input is required")

        optional_params = kwargs.get("optional_params")
        if optional_params is None or not isinstance(optional_params, dict):
            raise ValueError("optional_params is required")

        love_engine_params = kwargs.get("love_engine_params")
        if love_engine_params is None or not isinstance(love_engine_params, dict):
            raise ValueError("love_engine_params is required")

        headers = kwargs.get("headers")
        if headers is None or not isinstance(headers, dict):
            raise ValueError("headers is required")

        headers = kwargs.get("headers")
        if headers is None or not isinstance(headers, dict):
            raise ValueError("headers is required")

        logging_obj = kwargs.get("logging_obj")
        if logging_obj is None or not isinstance(logging_obj, LoveEngineLoggingObj):
            raise ValueError("logging_obj is required")

        return SpeechToCompletionBridgeHandlerInputKwargs(
            model=model,
            input=input,
            voice=kwargs.get("voice"),
            optional_params=optional_params,
            love_engine_params=love_engine_params,
            logging_obj=logging_obj,
            custom_llm_provider=custom_llm_provider,
            headers=headers,
        )

    def speech(
        self,
        model: str,
        input: str,
        voice: Optional[Union[str, dict]],
        optional_params: dict,
        love_engine_params: dict,
        headers: dict,
        logging_obj: "LoveEngineLoggingObj",
        custom_llm_provider: str,
    ) -> "HttpxBinaryResponseContent":
        received_args = locals()
        from love_engine import completion
        from love_engine.types.utils import ModelResponse

        validated_kwargs = self.validate_input_kwargs(received_args)
        model = validated_kwargs["model"]
        input = validated_kwargs["input"]
        optional_params = validated_kwargs["optional_params"]
        love_engine_params = validated_kwargs["love_engine_params"]
        headers = validated_kwargs["headers"]
        logging_obj = validated_kwargs["logging_obj"]
        custom_llm_provider = validated_kwargs["custom_llm_provider"]
        voice = validated_kwargs["voice"]

        request_data = self.transformation_handler.transform_request(
            model=model,
            input=input,
            optional_params=optional_params,
            love_engine_params=love_engine_params,
            headers=headers,
            love_engine_logging_obj=logging_obj,
            custom_llm_provider=custom_llm_provider,
            voice=voice,
        )

        result = completion(
            **request_data,
        )

        if isinstance(result, ModelResponse):
            return self.transformation_handler.transform_response(
                model_response=result,
            )
        else:
            raise Exception("Unmapped response type. Got type: {}".format(type(result)))


speech_to_completion_bridge_handler = SpeechToCompletionBridgeHandler()
