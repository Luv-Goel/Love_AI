"""
Helper functions for health check calls.
"""

from typing import TYPE_CHECKING, Callable, Dict, Literal, Optional

from love_engine.types.utils import LIST_BATCHES_SUPPORTED_PROVIDERS

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging

# Minimal PDF for health checks - base64 encoded 1-page PDF with just "test"
TEST_PDF_URL = "data:application/pdf;base64,JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBlIC9QYWdlCi9QYXJlbnQgMSAwIFIKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KL0NvbnRlbnRzIDQgMCBSCi9SZXNvdXJjZXMgPDwvRm9udCA8PC9GMSAyIDAgUj4+Pj4+PgplbmRvYmoKNCAwIG9iago8PC9MZW5ndGggNDQ+PgpzdHJlYW0KQlQKL0YxIDI0IFRmCjEwMCA3MDAgVGQKKHRlc3QpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKMiAwIG9iago8PC9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYT4+CmVuZG9iagoxIDAgb2JqCjw8L1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDE+PgplbmRvYmoKNSAwIG9iago8PC9UeXBlIC9DYXRhbG9nCi9QYWdlcyAxIDAgUj4+CmVuZG9iagp0cmFpbGVyCjw8L1NpemUgNgovUm9vdCA1IDAgUj4+CnN0YXJ0eHJlZgozMjQKJSVFT0Y="


class HealthCheckHelpers:
    @staticmethod
    async def ahealth_check_wildcard_models(
        model: str,
        custom_llm_provider: str,
        model_params: dict,
        love_engine_logging_obj: "Logging",
    ) -> dict:
        from love_engine import acompletion
        from love_engine.love_engine_core_utils.llm_request_utils import (
            pick_cheapest_chat_models_from_llm_provider,
        )

        # this is a wildcard model, we need to pick a random model from the provider
        cheapest_models = pick_cheapest_chat_models_from_llm_provider(
            custom_llm_provider=custom_llm_provider, n=3
        )
        if len(cheapest_models) == 0:
            raise Exception(
                f"Unable to health check wildcard model for provider {custom_llm_provider}. Add a model on your config.yaml or contribute here - https://github.com/BerriAI/love_engine/blob/main/model_prices_and_context_window.json"
            )
        if len(cheapest_models) > 1:
            fallback_models = cheapest_models[
                1:
            ]  # Pick the last 2 models from the shuffled list
        else:
            fallback_models = None
        model_params["model"] = cheapest_models[0]
        model_params["love_engine_logging_obj"] = love_engine_logging_obj
        model_params["fallbacks"] = fallback_models
        model_params["max_tokens"] = model_params.get(
            "max_tokens", 10
        )  # gpt-5-nano throws errors for max_tokens=1
        await acompletion(**model_params)
        return {}

    @staticmethod
    def _update_model_params_with_health_check_tracking_information(
        model_params: dict,
    ) -> dict:
        """
        Updates the health check model params with tracking information.

        The following is added at this stage:
            1. `tags`: This helps identify health check calls in the DB.
            2. `user_api_key_auth`: This helps identify health check calls in the DB.
                We need this since the DB requires an API Key to track a log in the SpendLogs Table
        """
        from love_engine.proxy._types import UserAPIKeyAuth
        from love_engine.proxy.love_engine_pre_call_utils import LoveEngineProxyRequestSetup

        _metadata_variable_name = "love_engine_metadata"
        love_engine_metadata = HealthCheckHelpers._get_metadata_for_health_check_call()
        model_params[_metadata_variable_name] = love_engine_metadata
        model_params = LoveEngineProxyRequestSetup.add_user_api_key_auth_to_request_metadata(
            data=model_params,
            user_api_key_dict=UserAPIKeyAuth.get_love_engine_internal_health_check_user_api_key_auth(),
            _metadata_variable_name=_metadata_variable_name,
        )
        return model_params

    @staticmethod
    def _get_metadata_for_health_check_call():
        """
        Returns the metadata for the health check call.
        """
        from love_engine.constants import LITTELM_INTERNAL_HEALTH_SERVICE_ACCOUNT_NAME

        return {
            "tags": [LITTELM_INTERNAL_HEALTH_SERVICE_ACCOUNT_NAME],
        }

    @staticmethod
    async def _batch_health_check(
        custom_llm_provider: str,
        model_params: dict,
        filtered_model_params: dict,
    ) -> dict:
        """
        Health check for batch mode.

        Calls list_batches for providers that support it (openai, hosted_vllm, azure,
        vertex_ai). For all other providers (e.g. bedrock) the batch API surface doesn't
        include list_batches, so we fall back to acompletion to verify connectivity and
        credential validity instead.
        """
        import love_engine

        if custom_llm_provider in LIST_BATCHES_SUPPORTED_PROVIDERS:
            return await love_engine.alist_batches(**filtered_model_params)
        else:
            return await love_engine.acompletion(**model_params)

    @staticmethod
    def get_mode_handlers(
        model: str,
        custom_llm_provider: str,
        model_params: dict,
        prompt: Optional[str] = None,
        input: Optional[list] = None,
    ) -> Dict[
        Literal[
            "chat",
            "completion",
            "embedding",
            "audio_speech",
            "audio_transcription",
            "image_generation",
            "video_generation",
            "rerank",
            "realtime",
            "batch",
            "responses",
            "ocr",
        ],
        Callable,
    ]:
        """
        Returns a dictionary of mode handlers for health check calls.

        Mode Handlers are Callables that need to be run for execution of the health check call.

        Args:
            model: The model name
            custom_llm_provider: The LLM provider
            model_params: The model parameters
            prompt: Optional prompt for health check
            input: Optional input for health check

        Returns:
            Dictionary mapping mode names to their handler functions
        """
        import love_engine
        from love_engine.love_engine_core_utils.audio_utils.utils import (
            get_audio_file_for_health_check,
        )
        from love_engine.love_engine_core_utils.health_check_utils import _filter_model_params
        from love_engine.realtime_api.main import _realtime_health_check

        return {
            "chat": lambda: love_engine.acompletion(
                **model_params,
            ),
            "completion": lambda: love_engine.atext_completion(
                **_filter_model_params(model_params=model_params),
                prompt=prompt or "test",
            ),
            "embedding": lambda: love_engine.aembedding(
                **_filter_model_params(model_params=model_params),
                input=input or ["test"],
            ),
            "audio_speech": lambda: love_engine.aspeech(
                **{
                    **_filter_model_params(model_params=model_params),
                    **(
                        {"voice": "alloy"}
                        if "voice"
                        not in _filter_model_params(model_params=model_params)
                        else {}
                    ),
                },
                input=prompt or "test",
            ),
            "audio_transcription": lambda: love_engine.atranscription(
                **_filter_model_params(model_params=model_params),
                file=get_audio_file_for_health_check(),
            ),
            "image_generation": lambda: love_engine.aimage_generation(
                **_filter_model_params(model_params=model_params),
                prompt=prompt,
            ),
            "video_generation": lambda: love_engine.avideo_generation(
                **_filter_model_params(model_params=model_params),
                prompt=prompt or "test video generation",
            ),
            "rerank": lambda: love_engine.arerank(
                **_filter_model_params(model_params=model_params),
                query=prompt or "",
                documents=["my sample text"],
            ),
            "realtime": lambda: _realtime_health_check(
                model=model,
                custom_llm_provider=custom_llm_provider,
                api_base=model_params.get("api_base", None),
                api_key=model_params.get("api_key", None),
                api_version=model_params.get("api_version", None),
            ),
            "batch": lambda: HealthCheckHelpers._batch_health_check(
                custom_llm_provider=custom_llm_provider,
                model_params=model_params,
                filtered_model_params=_filter_model_params(model_params=model_params),
            ),
            "responses": lambda: love_engine.aresponses(
                **_filter_model_params(model_params=model_params),
                input=prompt or "test",
            ),
            "ocr": lambda: love_engine.aocr(
                **_filter_model_params(model_params=model_params),
                document={
                    "type": "document_url",
                    "document_url": TEST_PDF_URL,
                },
            ),
        }
