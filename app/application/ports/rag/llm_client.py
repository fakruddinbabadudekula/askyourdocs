from abc import ABC, abstractmethod
from dataclasses import dataclass
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging
from logging import getLogger
from langchain_core.messages import AIMessage
import time
import asyncio
from app.core.exceptions import LLMServieException

logger = getLogger(__name__)


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    timeout: int = 40


class AsyncLLMClient(ABC):
    retry_config: RetryConfig
    retryable_excetpions: tuple[type[BaseException]]
    
    @abstractmethod
    async def call(self, prompt: str) -> AIMessage:
        pass

    async def invoke(self, prompt: str) -> AIMessage:
        @retry(
            stop=stop_after_attempt(self.retry_config.max_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=32),  # 2s, 4s, 8s, 16s, 32s
            retry=retry_if_exception_type(self.retryable_excetpions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,  # Raise the original exception after all retries fail
        )
        async def _invoke_with_retries() -> AIMessage:
            try:
                start = time.perf_counter()
                response = await asyncio.wait_for(
                    self.call(prompt), timeout=self.retry_config.timeout
                )
                duration = time.perf_counter() - start
                logger.info(
                    "response_is_generated_successfully", extra={"duration": duration}
                )
                return response
            except self.retryable_excetpions as e:
                logger.warning("llm_call_failed_retrying", extra={"error": str(e)})
                raise  # or do something

        try:
            return await _invoke_with_retries()
        except self.retryable_excetpions as e:
            raise LLMServieException(
                "llm_service failed to generate response after retries",
            ) from e
