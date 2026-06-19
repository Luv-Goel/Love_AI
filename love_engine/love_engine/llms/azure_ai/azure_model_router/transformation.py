"""
Transformation for Azure AI Foundry Model Router.

The Model Router is a special Azure AI deployment that automatically routes requests
to the best available model. It has specific cost tracking requirements.
"""

from typing import Any, List, Optional

from httpx import Response

from love_engine.llms.azure_ai.chat.transformation import AzureAIStudioConfig
from love_engine.llms.base_llm.chat.transformation import LoveEngineLoggingObj
from love_engine.types.llms.openai import AllMessageValues
from love_engine.types.utils import ModelResponse


class AzureModelRouterConfig(AzureAIStudioConfig):
    """
    Configuration for Azure AI Foundry Model Router.

    Handles:
    - Stripping model_router prefix before sending to Azure API
    - Preserving full model path in responses for cost tracking
    - Calculating flat infrastructure costs for Model Router
    """

    def transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        headers: dict,
    ) -> dict:
        """
        Transform request for Model Router.

        Strips the model_router/ prefix so only the deployment name is sent to Azure.
        Example: model_router/azure-model-router -> azure-model-router
        """
        from love_engine.llms.azure_ai.common_utils import AzureFoundryModelInfo

        # Get base model name (strips routing prefixes like model_router/)
        base_model: str = AzureFoundryModelInfo.get_base_model(model)

        return super().transform_request(
            base_model, messages, optional_params, love_engine_params, headers
        )

    def transform_response(
        self,
        model: str,
        raw_response: Response,
        model_response: ModelResponse,
        logging_obj: LoveEngineLoggingObj,
        request_data: dict,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        encoding: Any,
        api_key: Optional[str] = None,
        json_mode: Optional[bool] = None,
    ) -> ModelResponse:
        """
        Transform response for Model Router.

        Extracts the actual model used from the Azure response (e.g., gpt-5-nano-2025-08-07)
        and returns it with the azure_ai/ prefix for proper display and cost tracking.
        """
        from love_engine.llms.azure_ai.common_utils import AzureFoundryModelInfo

        # Get base model for the parent call (strips routing prefixes for API compatibility)
        base_model: str = AzureFoundryModelInfo.get_base_model(model)

        # Call parent transform_response first - this will extract the actual model
        # from the raw response (e.g., "gpt-5-nano-2025-08-07")
        model_response = super().transform_response(
            model=base_model,
            raw_response=raw_response,
            model_response=model_response,
            logging_obj=logging_obj,
            request_data=request_data,
            messages=messages,
            optional_params=optional_params,
            love_engine_params=love_engine_params,
            encoding=encoding,
            api_key=api_key,
            json_mode=json_mode,
        )
        return model_response

    def calculate_additional_costs(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> Optional[dict]:
        """
        Calculate additional costs for Azure Model Router.

        Adds a flat infrastructure cost of $0.14 per M input tokens for using the Model Router.

        Args:
            model: The model name (should be a model router model)
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Dictionary with additional costs, or None if not applicable.
        """
        from love_engine.llms.azure_ai.cost_calculator import (
            calculate_azure_model_router_flat_cost,
        )

        flat_cost = calculate_azure_model_router_flat_cost(
            model=model, prompt_tokens=prompt_tokens
        )

        if flat_cost > 0:
            return {"Azure Model Router Flat Cost": flat_cost}

        return None
