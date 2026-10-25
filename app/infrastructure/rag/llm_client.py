from app.application.ports.rag.llm_client import AsyncLLMClient, RetryConfig
from openai import (
    APIError,
    RateLimitError,
)
from langchain_core.language_models.chat_models import BaseChatModel

import asyncio


class OpenRouterLLMClient(AsyncLLMClient):
    def __init__(self, retry_config: RetryConfig, llm: BaseChatModel):
        self.retry_config = retry_config
        self.retryable_excetpions = (
            ConnectionError,
            asyncio.TimeoutError,
            RateLimitError,
            APIError,
        )
        self._llm = llm

    async def call(self, prompt):
        return await self._llm.ainvoke(prompt)
