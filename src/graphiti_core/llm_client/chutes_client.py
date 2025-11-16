"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import typing
from types import SimpleNamespace

import aiohttp
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from .config import DEFAULT_MAX_TOKENS, LLMConfig
from .errors import RateLimitError
from .openai_base_client import DEFAULT_REASONING, DEFAULT_VERBOSITY, BaseOpenAIClient


class ChutesClient(BaseOpenAIClient):
    """
    ChutesClient is a client class for interacting with Chutes's language models.
    """

    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        client: typing.Any = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        reasoning: str = DEFAULT_REASONING,
        verbosity: str = DEFAULT_VERBOSITY,
    ):
        """
        Initialize the ChutesClient with the provided configuration, cache setting, and client.
        """
        super().__init__(config, cache, max_tokens, reasoning, verbosity)

        if config is None:
            config = LLMConfig()

        self.api_key = config.api_key
        self.base_url = "https://llm.chutes.ai/v1"

    async def _create_structured_completion(
        self,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None,
        max_tokens: int,
        response_model: type[BaseModel],
        reasoning: str | None = None,
        verbosity: str | None = None,
    ):
        """Create a structured completion using Chutes's API."""
        return await self._create_completion(
            model, messages, temperature, max_tokens, response_model
        )

    async def _create_completion(
        self,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None,
        max_tokens: int,
        response_model: type[BaseModel] | None = None,
        reasoning: str | None = None,
        verbosity: str | None = None,
    ):
        """Create a regular completion with JSON format."""

        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,  # The base client doesn't support streaming
        }
        if response_model:
            body["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                f"{self.base_url}/chat/completions", json=body
            ) as response:
                if response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                response.raise_for_status()
                response_json = await response.json()

                content = response_json["choices"][0]["message"]["content"]

                # Create a mock object that mimics the OpenAI response structure
                mock_message = SimpleNamespace(content=content)
                mock_choice = SimpleNamespace(message=mock_message)
                mock_response = SimpleNamespace(choices=[mock_choice])

                return mock_response