"""
Callbacks triggered on cooling down deployments
"""

import copy
from typing import TYPE_CHECKING, Any, Optional, Union

import love_engine
from love_engine._logging import verbose_logger

if TYPE_CHECKING:
    from love_engine.router import Router as _Router

    LoveEngineRouter = _Router
    from love_engine.integrations.prometheus import PrometheusLogger
else:
    LoveEngineRouter = Any
    PrometheusLogger = Any


async def router_cooldown_event_callback(
    love_engine_router_instance: LoveEngineRouter,
    deployment_id: str,
    exception_status: Union[str, int],
    cooldown_time: Optional[float],
):
    """
    Callback triggered when a deployment is put into cooldown by love_engine

    - Updates deployment state on Prometheus
    - Increments cooldown metric for deployment on Prometheus
    """
    verbose_logger.debug("In router_cooldown_event_callback - updating prometheus")
    _deployment = love_engine_router_instance.get_deployment(model_id=deployment_id)
    if _deployment is None:
        verbose_logger.warning(
            f"in router_cooldown_event_callback but _deployment is None for deployment_id={deployment_id}. Doing nothing"
        )
        return
    _love_engine_params = _deployment["love_engine_params"]
    temp_love_engine_params = copy.deepcopy(_love_engine_params)
    temp_love_engine_params = dict(temp_love_engine_params)
    _model_name = _deployment.get("model_name", None) or ""
    _api_base = (
        love_engine.get_api_base(model=_model_name, optional_params=temp_love_engine_params)
        or ""
    )
    model_info = _deployment["model_info"]
    model_id = model_info.id

    love_engine_model_name = temp_love_engine_params.get("model") or ""
    llm_provider = ""
    try:
        _, llm_provider, _, _ = love_engine.get_llm_provider(
            model=love_engine_model_name,
            custom_llm_provider=temp_love_engine_params.get("custom_llm_provider"),
        )
    except Exception:
        pass

    # get the prometheus logger from in memory loggers
    prometheusLogger: Optional[PrometheusLogger] = (
        _get_prometheus_logger_from_callbacks()
    )

    if prometheusLogger is not None:
        prometheusLogger.set_deployment_complete_outage(
            love_engine_model_name=_model_name,
            model_id=model_id,
            api_base=_api_base,
            api_provider=llm_provider,
        )

        prometheusLogger.increment_deployment_cooled_down(
            love_engine_model_name=_model_name,
            model_id=model_id,
            api_base=_api_base,
            api_provider=llm_provider,
            exception_status=str(exception_status),
        )

    return


def _get_prometheus_logger_from_callbacks() -> Optional[PrometheusLogger]:
    """
    Checks if prometheus is a initalized callback, if yes returns it
    """
    from love_engine.integrations.prometheus import PrometheusLogger

    if PrometheusLogger is None:
        return None

    for _callback in love_engine._async_success_callback:
        if isinstance(_callback, PrometheusLogger):
            return _callback
    for global_callback in love_engine.callbacks:
        if isinstance(global_callback, PrometheusLogger):
            return global_callback

    return None
