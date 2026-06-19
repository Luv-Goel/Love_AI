"""
Config table model.

Canonical definition for ``love_engine_config``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from typing import Dict

from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_Config(LoveEnginePydanticObjectBase):
    param_name: str
    param_value: Dict
