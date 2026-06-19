from typing import Literal, Optional

import love_engine
from love_engine.exceptions import BadRequestError
from love_engine.types.utils import LlmProviders, LlmProvidersSet


def get_supported_openai_params(
    model: str,
    custom_llm_provider: Optional[str] = None,
    request_type: Literal[
        "chat_completion", "embeddings", "transcription"
    ] = "chat_completion",
    base_model: Optional[str] = None,
) -> Optional[list]:
    """
    Returns the supported openai params for a given model + provider

    Example:
    ```
    get_supported_openai_params(model="anthropic.claude-3", custom_llm_provider="bedrock")
    ```

    Args:
        base_model: An optional capability hint for deployments whose ``model``
            label isn't recognized on its own (e.g. an Azure deployment name, or a
            friendly Bedrock alias). It is additive: the result is the union of the
            params supported by ``model`` and by ``base_model``, so a hint can only
            add capabilities, never strip ones the real model already supports.

    Returns:
    - List if custom_llm_provider is mapped
    - None if unmapped
    """
    if not custom_llm_provider:
        try:
            custom_llm_provider = love_engine.get_llm_provider(model=model)[1]
        except BadRequestError:
            return None

    if custom_llm_provider in LlmProvidersSet:
        provider_config = love_engine.ProviderConfigManager.get_provider_chat_config(
            model=model,
            provider=LlmProviders(custom_llm_provider),
            base_model=base_model,
        )
    elif custom_llm_provider.split("/")[0] in LlmProvidersSet:
        provider_config = love_engine.ProviderConfigManager.get_provider_chat_config(
            model=model,
            provider=LlmProviders(custom_llm_provider.split("/")[0]),
            base_model=base_model,
        )
    else:
        provider_config = None

    if provider_config and request_type == "chat_completion":
        supported_params = provider_config.get_supported_openai_params(model=model)
        if base_model and base_model != model:
            base_model_params = provider_config.get_supported_openai_params(
                model=base_model
            )
            supported_params = list(
                dict.fromkeys([*supported_params, *base_model_params])
            )
        return supported_params

    if custom_llm_provider == "bedrock":
        return love_engine.AmazonConverseConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "meta_llama":
        provider_config = love_engine.ProviderConfigManager.get_provider_chat_config(
            model=model, provider=LlmProviders.LLAMA
        )
        if provider_config:
            return provider_config.get_supported_openai_params(model=model)
    elif custom_llm_provider == "ollama":
        return love_engine.OllamaConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "ollama_chat":
        return love_engine.OllamaChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "anthropic":
        return love_engine.AnthropicConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "anthropic_text":
        return love_engine.AnthropicTextConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "fireworks_ai":
        if request_type == "embeddings":
            return love_engine.FireworksAIEmbeddingConfig().get_supported_openai_params(
                model=model
            )
        elif request_type == "transcription":
            return love_engine.FireworksAIAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
        else:
            return love_engine.FireworksAIConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nvidia_nim":
        if request_type == "chat_completion":
            return love_engine.nvidiaNimConfig.get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return love_engine.nvidiaNimEmbeddingConfig.get_supported_openai_params()
    elif custom_llm_provider == "cerebras":
        return love_engine.CerebrasConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "baseten":
        return love_engine.BasetenConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "xai":
        return love_engine.XAIChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "ai21_chat" or custom_llm_provider == "ai21":
        return love_engine.AI21ChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "volcengine":
        return love_engine.VolcEngineConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "groq":
        return love_engine.GroqChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "bedrock_mantle":
        return love_engine.BedrockMantleChatConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "hosted_vllm":
        return love_engine.HostedVLLMChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "vllm":
        return love_engine.VLLMConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "deepseek":
        return love_engine.DeepSeekChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "cohere_chat" or custom_llm_provider == "cohere":
        return love_engine.CohereChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "maritalk":
        return love_engine.MaritalkConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "openai":
        if request_type == "transcription":
            transcription_provider_config = (
                love_engine.ProviderConfigManager.get_provider_audio_transcription_config(
                    model=model, provider=LlmProviders.OPENAI
                )
            )
            if isinstance(
                transcription_provider_config, love_engine.OpenAIGPTAudioTranscriptionConfig
            ):
                return transcription_provider_config.get_supported_openai_params(
                    model=model
                )
            else:
                raise ValueError(
                    f"Unsupported provider config: {transcription_provider_config} for model: {model}"
                )
        return love_engine.OpenAIConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "sap":
        if request_type == "chat_completion":
            return love_engine.GenAIHubOrchestrationConfig().get_supported_openai_params(
                model=model
            )
        elif request_type == "embeddings":
            return love_engine.GenAIHubEmbeddingConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider == "azure":
        _azure_detection_model = base_model or model
        if love_engine.AzureOpenAIO1Config().is_o_series_model(
            model=_azure_detection_model
        ):
            return love_engine.AzureOpenAIO1Config().get_supported_openai_params(
                model=_azure_detection_model
            )
        elif love_engine.AzureOpenAIGPT5Config.is_model_gpt_5_model(
            model=_azure_detection_model
        ):
            return love_engine.AzureOpenAIGPT5Config().get_supported_openai_params(
                model=_azure_detection_model
            )
        else:
            return love_engine.AzureOpenAIConfig().get_supported_openai_params(
                model=_azure_detection_model
            )
    elif custom_llm_provider == "openrouter":
        return love_engine.OpenrouterConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "vercel_ai_gateway":
        return love_engine.VercelAIGatewayConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "mistral" or custom_llm_provider == "codestral":
        # mistal and codestral api have the exact same params
        if request_type == "chat_completion":
            return love_engine.MistralConfig().get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return love_engine.MistralEmbeddingConfig().get_supported_openai_params()
        elif request_type == "transcription":
            from love_engine.llms.mistral.audio_transcription.transformation import (
                MistralAudioTranscriptionConfig,
            )

            return MistralAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider == "text-completion-codestral":
        return love_engine.CodestralTextCompletionConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "sambanova":
        if request_type == "embeddings":
            love_engine.SambaNovaEmbeddingConfig().get_supported_openai_params(model=model)
        else:
            return love_engine.SambanovaConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nebius":
        if request_type == "chat_completion":
            return love_engine.NebiusConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "wandb":
        if request_type == "chat_completion":
            return love_engine.WandbConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "replicate":
        return love_engine.ReplicateConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "huggingface":
        return love_engine.HuggingFaceChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "jina_ai":
        if request_type == "embeddings":
            return love_engine.JinaAIEmbeddingConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider == "together_ai":
        return love_engine.TogetherAIConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "databricks":
        if request_type == "chat_completion":
            return love_engine.DatabricksConfig().get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return love_engine.DatabricksEmbeddingConfig().get_supported_openai_params()
    elif custom_llm_provider == "palm" or custom_llm_provider == "gemini":
        return love_engine.GoogleAIStudioGeminiConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "novita":
        return love_engine.NovitaConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "vertex_ai" or custom_llm_provider == "vertex_ai_beta":
        if request_type == "chat_completion":
            if model.startswith("mistral"):
                return love_engine.MistralConfig().get_supported_openai_params(model=model)
            elif model.startswith("codestral"):
                return (
                    love_engine.CodestralTextCompletionConfig().get_supported_openai_params(
                        model=model
                    )
                )
            elif model.startswith("claude"):
                return love_engine.VertexAIAnthropicConfig().get_supported_openai_params(
                    model=model
                )
            elif model.startswith("gemini"):
                return love_engine.VertexGeminiConfig().get_supported_openai_params(
                    model=model
                )
            else:
                return love_engine.VertexAILlama3Config().get_supported_openai_params(
                    model=model
                )
        elif request_type == "embeddings":
            return love_engine.VertexAITextEmbeddingConfig().get_supported_openai_params()
    elif custom_llm_provider == "sagemaker":
        return love_engine.SagemakerConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "aleph_alpha":
        return [
            "max_tokens",
            "stream",
            "top_p",
            "temperature",
            "presence_penalty",
            "frequency_penalty",
            "n",
            "stop",
        ]
    elif custom_llm_provider == "cloudflare":
        return love_engine.CloudflareChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nlp_cloud":
        return love_engine.NLPCloudConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "petals":
        return love_engine.PetalsConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "deepinfra":
        return love_engine.DeepInfraConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "perplexity":
        return love_engine.PerplexityChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "nscale":
        return love_engine.NscaleConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "anyscale":
        return [
            "temperature",
            "top_p",
            "stream",
            "max_tokens",
            "stop",
            "frequency_penalty",
            "presence_penalty",
        ]
    elif custom_llm_provider == "watsonx":
        return love_engine.IBMWatsonXChatConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "watsonx_text":
        return love_engine.IBMWatsonXAIConfig().get_supported_openai_params(model=model)
    elif (
        custom_llm_provider == "custom_openai"
        or custom_llm_provider == "text-completion-openai"
    ):
        return love_engine.OpenAITextCompletionConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "predibase":
        return love_engine.PredibaseConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "voyage":
        if (
            request_type == "embeddings"
            and love_engine.VoyageMultimodalEmbeddingConfig.is_multimodal_embeddings(model)
        ):
            return (
                love_engine.VoyageMultimodalEmbeddingConfig().get_supported_openai_params(
                    model=model
                )
            )
        return love_engine.VoyageEmbeddingConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "infinity":
        return love_engine.InfinityEmbeddingConfig().get_supported_openai_params(
            model=model
        )
    elif custom_llm_provider == "triton":
        if request_type == "embeddings":
            return love_engine.TritonEmbeddingConfig().get_supported_openai_params(
                model=model
            )
        else:
            return love_engine.TritonConfig().get_supported_openai_params(model=model)
    elif custom_llm_provider == "deepgram":
        if request_type == "transcription":
            return (
                love_engine.DeepgramAudioTranscriptionConfig().get_supported_openai_params(
                    model=model
                )
            )
    elif custom_llm_provider == "ovhcloud":
        if request_type == "transcription":
            from love_engine.llms.ovhcloud.audio_transcription.transformation import (
                OVHCloudAudioTranscriptionConfig,
            )

            return OVHCloudAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider == "scaleway":
        if request_type == "transcription":
            from love_engine.llms.scaleway.audio_transcription.transformation import (
                ScalewayAudioTranscriptionConfig,
            )

            return ScalewayAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider == "elevenlabs":
        if request_type == "transcription":
            from love_engine.llms.elevenlabs.audio_transcription.transformation import (
                ElevenLabsAudioTranscriptionConfig,
            )

            return ElevenLabsAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider == "soniox":
        if request_type == "transcription":
            return love_engine.SonioxAudioTranscriptionConfig().get_supported_openai_params(
                model=model
            )
    elif custom_llm_provider in love_engine._custom_providers:
        if request_type == "chat_completion":
            provider_config = love_engine.ProviderConfigManager.get_provider_chat_config(
                model=model, provider=LlmProviders.CUSTOM
            )
            if provider_config:
                return provider_config.get_supported_openai_params(model=model)
        elif request_type == "embeddings":
            return None
        elif request_type == "transcription":
            return None

    return None
