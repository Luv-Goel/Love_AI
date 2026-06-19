"""
Qostodian Nexus (by Qohash) — LoveEngine guardrail integration.
"""

import os
from typing import TYPE_CHECKING, Literal, Optional, Type

from love_engine.integrations.custom_guardrail import log_guardrail_information
from love_engine.proxy.guardrails.guardrail_hooks.generic_guardrail_api.generic_guardrail_api import (
    GenericGuardrailAPI,
)
from love_engine.types.proxy.guardrails.guardrail_hooks.qohash import (
    QostodianNexusConfigModel,
)
from love_engine.types.utils import GenericGuardrailAPIInputs

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj

GUARDRAIL_NAME = "qostodian_nexus"


class QostodianNexus(GenericGuardrailAPI):
    def __init__(
        self,
        api_base: Optional[str] = None,
        **kwargs,
    ):
        api_base = api_base or os.environ.get(
            "QOSTODIAN_NEXUS_API_BASE", "http://nexus:8800"
        )

        kwargs["guardrail_name"] = kwargs.get("guardrail_name", GUARDRAIL_NAME)

        # Merge built-in Qostodian Nexus identifier headers with any caller-supplied extra_headers
        nexus_headers = [
            "x-qostodian-nexus-identifiers-trace",
            "x-qostodian-nexus-identifiers-source",
            "x-qostodian-nexus-identifiers-container",
            "x-qostodian-nexus-identifiers-identity",
        ]

        existing = kwargs.get("extra_headers") or []
        kwargs["extra_headers"] = nexus_headers + [
            h for h in existing if h not in nexus_headers
        ]

        super().__init__(
            api_base=api_base,
            **kwargs,
        )

    @log_guardrail_information
    async def apply_guardrail(
        self,
        inputs: GenericGuardrailAPIInputs,
        request_data: dict,
        input_type: Literal["request", "response"],
        logging_obj: Optional["LoveEngineLoggingObj"] = None,
    ) -> GenericGuardrailAPIInputs:
        """
        Apply Qostodian Nexus to the given inputs.

        NOTE: This override is intentionally a pass-through. It must be present
        directly in this class's __dict__ so that LoveEngine's unified guardrail
        routing check (`"apply_guardrail" in type(callback).__dict__` in
        love_engine/proxy/utils.py) routes calls correctly. Do not remove.
        """
        return await super().apply_guardrail(
            inputs=inputs,
            request_data=request_data,
            input_type=input_type,
            logging_obj=logging_obj,
        )

    @classmethod
    def get_config_model(cls) -> Optional[Type[QostodianNexusConfigModel]]:
        """
        Returns the config model for Qostodian Nexus.
        """
        return QostodianNexusConfigModel
