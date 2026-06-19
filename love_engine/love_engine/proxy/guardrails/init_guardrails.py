from typing import Any, Dict, List, Optional, cast

import love_engine
from love_engine import Router
from love_engine._logging import verbose_proxy_logger
from love_engine.proxy.common_utils.callback_utils import initialize_callbacks_on_proxy

# v2 implementation
from love_engine.types.guardrails import Guardrail, GuardrailItem, GuardrailItemSpec

all_guardrails: List[GuardrailItem] = []

"""
Map guardrail_name: <pre_call>, <post_call>, during_call

"""


def init_guardrails_v2(
    all_guardrails: List[Dict],
    config_file_path: Optional[str] = None,
    llm_router: Optional[Router] = None,
):
    from love_engine.proxy.guardrails.guardrail_registry import IN_MEMORY_GUARDRAIL_HANDLER

    guardrail_list: List[Guardrail] = []

    for guardrail in all_guardrails:
        initialized_guardrail = IN_MEMORY_GUARDRAIL_HANDLER.initialize_guardrail(
            guardrail=cast(Guardrail, guardrail),
            config_file_path=config_file_path,
            llm_router=llm_router,
            source="config",
        )
        if initialized_guardrail:
            guardrail_list.append(initialized_guardrail)

    # verbose_proxy_logger.debug(f"\nGuardrail List:{guardrail_list}\n")

    # Populate router's guardrail_list for load balancing support
    _populate_router_guardrail_list(guardrail_list=guardrail_list)


def _populate_router_guardrail_list(guardrail_list: List[Guardrail]) -> None:
    """
    Populate the router's guardrail_list from initialized guardrails.

    This enables load balancing across multiple guardrail deployments
    with the same guardrail_name.
    """
    from love_engine.proxy.guardrails.guardrail_registry import IN_MEMORY_GUARDRAIL_HANDLER
    from love_engine.proxy.proxy_server import llm_router
    from love_engine.types.router import GuardrailTypedDict

    if llm_router is None:
        verbose_proxy_logger.debug(
            "Router not initialized yet, skipping guardrail_list population"
        )
        return

    router_guardrail_list: List[GuardrailTypedDict] = []

    for guardrail in guardrail_list:
        guardrail_id = guardrail.get("guardrail_id")
        guardrail_name = guardrail.get("guardrail_name")
        love_engine_params: Any = guardrail.get("love_engine_params", {})

        # Get the callback instance from the registry
        callback = None
        if guardrail_id:
            callback = IN_MEMORY_GUARDRAIL_HANDLER.guardrail_id_to_custom_guardrail.get(
                guardrail_id
            )

        # Build love_engine_params dict for the router
        params_dict = (
            love_engine_params.model_dump()
            if hasattr(love_engine_params, "model_dump")
            else dict(love_engine_params)
        )

        router_guardrail: GuardrailTypedDict = GuardrailTypedDict(
            guardrail_name=guardrail_name or "",
            love_engine_params={
                "guardrail": params_dict.get("guardrail", ""),
                "mode": params_dict.get("mode", ""),
                "api_key": params_dict.get("api_key"),
                "api_base": params_dict.get("api_base"),
            },
            callback=callback,
            id=guardrail_id,
        )

        router_guardrail_list.append(router_guardrail)

    llm_router.guardrail_list = router_guardrail_list
    verbose_proxy_logger.debug(
        f"Populated router guardrail_list with {len(router_guardrail_list)} guardrails"
    )


### LEGACY IMPLEMENTATION ###
def initialize_guardrails(
    guardrails_config: List[Dict[str, GuardrailItemSpec]],
    premium_user: bool,
    config_file_path: str,
    love_engine_settings: dict,
) -> Dict[str, GuardrailItem]:
    try:
        verbose_proxy_logger.debug(f"validating  guardrails passed {guardrails_config}")
        global all_guardrails
        for item in guardrails_config:
            """
            one item looks like this:

            {'prompt_injection': {'callbacks': ['lakera_prompt_injection', 'prompt_injection_api_2'], 'default_on': True, 'enabled_roles': ['user']}}
            """
            for k, v in item.items():
                guardrail_item = GuardrailItem(**v, guardrail_name=k)
                all_guardrails.append(guardrail_item)
                love_engine.guardrail_name_config_map[k] = guardrail_item

        # set appropriate callbacks if they are default on
        default_on_callbacks = set()
        callback_specific_params = {}
        for guardrail in all_guardrails:
            verbose_proxy_logger.debug(guardrail.guardrail_name)
            verbose_proxy_logger.debug(guardrail.default_on)

            callback_specific_params.update(guardrail.callback_args)

            if guardrail.default_on is True:
                # add these to love_engine callbacks if they don't exist
                for callback in guardrail.callbacks:
                    if callback not in love_engine.callbacks:
                        default_on_callbacks.add(callback)

                    if guardrail.logging_only is True:
                        if callback == "presidio":
                            callback_specific_params["presidio"] = {"logging_only": True}  # type: ignore

        default_on_callbacks_list = list(default_on_callbacks)
        if len(default_on_callbacks_list) > 0:
            initialize_callbacks_on_proxy(
                value=default_on_callbacks_list,
                premium_user=premium_user,
                config_file_path=config_file_path,
                love_engine_settings=love_engine_settings,
                callback_specific_params=callback_specific_params,
            )

        return love_engine.guardrail_name_config_map
    except Exception as e:
        verbose_proxy_logger.exception(
            "error initializing guardrails {}".format(str(e))
        )
        raise e
