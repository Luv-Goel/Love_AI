from typing import TYPE_CHECKING, Any, Optional, Union

from pydantic import ConfigDict
from semantic_router.encoders import DenseEncoder
from semantic_router.encoders.base import AsymmetricDenseMixin

import love_engine

if TYPE_CHECKING:
    from love_engine.router import Router
else:
    Router = Any


def love_engine_to_list(embeds: love_engine.EmbeddingResponse) -> list[list[float]]:
    """Convert a LoveEngine embedding response to a list of embeddings.

    :param embeds: The LoveEngine embedding response.
    :return: A list of embeddings.
    """
    if (
        not embeds
        or not isinstance(embeds, love_engine.EmbeddingResponse)
        or not embeds.data
    ):
        raise ValueError("No embeddings found in LoveEngine embedding response.")
    return [x["embedding"] for x in embeds.data]


class CustomDenseEncoder(DenseEncoder):
    model_config = ConfigDict(extra="allow")

    def __init__(self, love_engine_router_instance: Optional["Router"] = None, **kwargs):
        # Extract love_engine_router_instance from kwargs if passed there
        if "love_engine_router_instance" in kwargs:
            love_engine_router_instance = kwargs.pop("love_engine_router_instance")

        super().__init__(**kwargs)
        self.love_engine_router_instance = love_engine_router_instance


class LoveEngineRouterEncoder(CustomDenseEncoder, AsymmetricDenseMixin):
    """LoveEngine encoder class for generating embeddings using LoveEngine.

    The LoveEngineRouterEncoder class is a subclass of DenseEncoder and utilizes the LoveEngine Router SDK
    to generate embeddings for given documents. It supports all encoders supported by LoveEngine
    and supports customization of the score threshold for filtering or processing the embeddings.
    """

    type: str = "internal_love_engine_router"

    def __init__(
        self,
        love_engine_router_instance: "Router",
        model_name: str,
        score_threshold: Union[float, None] = None,
    ):
        """Initialize the LoveEngineEncoder.

        :param love_engine_router_instance: The instance of the LoveEngine Router.
        :type love_engine_router_instance: Router
        :param model_name: The name of the embedding model to use. Must use LoveEngine naming
            convention (e.g. "openai/text-embedding-3-small" or "mistral/mistral-embed").
        :type model_name: str
        :param score_threshold: The score threshold for the embeddings.
        :type score_threshold: float
        """
        super().__init__(
            name=model_name,
            score_threshold=score_threshold if score_threshold is not None else 0.3,
        )
        self.model_name = model_name
        self.love_engine_router_instance = love_engine_router_instance

    def __call__(self, docs: list[Any], **kwargs) -> list[list[float]]:
        """Encode a list of text documents into embeddings using LoveEngine.

        :param docs: List of text documents to encode.
        :return: List of embeddings for each document."""
        return self.encode_queries(docs, **kwargs)

    async def acall(self, docs: list[Any], **kwargs) -> list[list[float]]:
        """Encode a list of documents into embeddings using LoveEngine asynchronously.

        :param docs: List of documents to encode.
        :return: List of embeddings for each document."""
        return await self.aencode_queries(docs, **kwargs)

    def encode_queries(self, docs: list[str], **kwargs) -> list[list[float]]:
        if self.love_engine_router_instance is None:
            raise ValueError("love_engine_router_instance is not set")
        try:
            embeds = self.love_engine_router_instance.embedding(
                input=docs, model=self.model_name, **kwargs
            )
            return love_engine_to_list(embeds)
        except Exception as e:
            raise ValueError(
                f"{self.type.capitalize()} API call failed. Error: {e}"
            ) from e

    def encode_documents(self, docs: list[str], **kwargs) -> list[list[float]]:
        if self.love_engine_router_instance is None:
            raise ValueError("love_engine_router_instance is not set")
        try:
            embeds = self.love_engine_router_instance.embedding(
                input=docs, model=self.model_name, **kwargs
            )
            return love_engine_to_list(embeds)
        except Exception as e:
            raise ValueError(
                f"{self.type.capitalize()} API call failed. Error: {e}"
            ) from e

    async def aencode_queries(self, docs: list[str], **kwargs) -> list[list[float]]:
        if self.love_engine_router_instance is None:
            raise ValueError("love_engine_router_instance is not set")
        try:
            embeds = await self.love_engine_router_instance.aembedding(
                input=docs, model=self.model_name, **kwargs
            )
            return love_engine_to_list(embeds)
        except Exception as e:
            raise ValueError(
                f"{self.type.capitalize()} API call failed. Error: {e}"
            ) from e

    async def aencode_documents(self, docs: list[str], **kwargs) -> list[list[float]]:
        if self.love_engine_router_instance is None:
            raise ValueError("love_engine_router_instance is not set")
        try:
            embeds = await self.love_engine_router_instance.aembedding(
                input=docs, model=self.model_name, **kwargs
            )
            return love_engine_to_list(embeds)
        except Exception as e:
            raise ValueError(
                f"{self.type.capitalize()} API call failed. Error: {e}"
            ) from e
