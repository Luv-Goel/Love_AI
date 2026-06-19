import asyncio
from typing import TYPE_CHECKING, Any

from love_engine.utils import calculate_max_parallel_requests

if TYPE_CHECKING:
    from love_engine.router import Router as _Router

    LoveEngineRouter = _Router
else:
    LoveEngineRouter = Any


class InitalizeCachedClient:
    @staticmethod
    def set_max_parallel_requests_client(
        love_engine_router_instance: LoveEngineRouter, model: dict
    ):
        love_engine_params = model.get("love_engine_params", {})
        model_id = model["model_info"]["id"]
        rpm = love_engine_params.get("rpm", None)
        tpm = love_engine_params.get("tpm", None)
        max_parallel_requests = love_engine_params.get("max_parallel_requests", None)
        calculated_max_parallel_requests = calculate_max_parallel_requests(
            rpm=rpm,
            max_parallel_requests=max_parallel_requests,
            tpm=tpm,
            default_max_parallel_requests=love_engine_router_instance.default_max_parallel_requests,
        )
        if calculated_max_parallel_requests:
            semaphore = asyncio.Semaphore(calculated_max_parallel_requests)
            cache_key = f"{model_id}_max_parallel_requests_client"
            love_engine_router_instance.cache.set_cache(
                key=cache_key,
                value=semaphore,
                local_only=True,
            )
