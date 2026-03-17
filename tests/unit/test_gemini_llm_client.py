"""Tests for platform LLM client — Gemini + Anthropic provider support."""

from unittest.mock import AsyncMock, patch

import pytest
from app.services.agents.llm_client import (
    _parse_json_response,
    generate_structured,
)


class TestJsonParsing:
    """Test JSON response parsing from various LLM outputs."""

    def test_plain_json(self):
        result = _parse_json_response('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_with_markdown_fence(self):
        result = _parse_json_response('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_json_with_triple_backtick(self):
        result = _parse_json_response('```\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_empty_string_returns_none(self):
        assert _parse_json_response("") is None

    def test_invalid_json_returns_none(self):
        assert _parse_json_response("not json") is None

    def test_non_dict_returns_none(self):
        assert _parse_json_response("[1, 2, 3]") is None

    def test_nested_json(self):
        text = '{"gaps_and_risks": ["gap1", "gap2"], "count": 3}'
        result = _parse_json_response(text)
        assert result["gaps_and_risks"] == ["gap1", "gap2"]
        assert result["count"] == 3


class TestProviderSelection:
    """Test provider selection logic."""

    @pytest.mark.asyncio
    async def test_no_keys_returns_none(self):
        with (
            patch("app.services.agents.llm_client.GEMINI_API_KEY", ""),
            patch("app.services.agents.llm_client.ANTHROPIC_API_KEY", ""),
        ):
            result = await generate_structured("system", "user")
        assert result is None

    @pytest.mark.asyncio
    async def test_gemini_preferred_when_configured(self):
        mock_gemini = AsyncMock(return_value={"test": "value"})
        with (
            patch("app.services.agents.llm_client.LLM_PROVIDER", "gemini"),
            patch("app.services.agents.llm_client.GEMINI_API_KEY", "test-key"),
            patch("app.services.agents.llm_client._call_gemini", mock_gemini),
        ):
            result = await generate_structured("system", "user")
        mock_gemini.assert_called_once_with("system", "user")
        assert result == {"test": "value"}

    @pytest.mark.asyncio
    async def test_anthropic_when_configured(self):
        mock_anthropic = AsyncMock(return_value={"test": "claude"})
        with (
            patch("app.services.agents.llm_client.LLM_PROVIDER", "anthropic"),
            patch("app.services.agents.llm_client.ANTHROPIC_API_KEY", "test-key"),
            patch("app.services.agents.llm_client._call_anthropic", mock_anthropic),
        ):
            result = await generate_structured("system", "user")
        mock_anthropic.assert_called_once_with("system", "user")
        assert result == {"test": "claude"}

    @pytest.mark.asyncio
    async def test_fallback_to_available_provider(self):
        """If configured provider has no key, fall back to available one."""
        mock_anthropic = AsyncMock(return_value={"fallback": True})
        with (
            patch("app.services.agents.llm_client.LLM_PROVIDER", "gemini"),
            patch("app.services.agents.llm_client.GEMINI_API_KEY", ""),
            patch("app.services.agents.llm_client.ANTHROPIC_API_KEY", "key"),
            patch("app.services.agents.llm_client._call_anthropic", mock_anthropic),
        ):
            result = await generate_structured("system", "user")
        assert result == {"fallback": True}


class TestPromptVersion:
    """Verify prompt version is tracked."""

    def test_prompt_version_exists(self):
        from app.services.agents.llm_client import PROMPT_VERSION

        assert PROMPT_VERSION == "v1.0"


class TestGeminiResponseFormat:
    """Test Gemini-specific response structure handling."""

    @pytest.mark.asyncio
    async def test_gemini_uses_json_mime_type(self):
        """Verify Gemini request includes responseMimeType for structured output."""
        import httpx

        captured_json = {}

        async def mock_post(url, **kwargs):
            captured_json.update(kwargs.get("json", {}))
            resp = httpx.Response(
                200,
                json={
                    "candidates": [
                        {
                            "content": {
                                "parts": [{"text": '{"test": "ok"}'}],
                            }
                        }
                    ],
                    "usageMetadata": {
                        "promptTokenCount": 10,
                        "candidatesTokenCount": 5,
                        "totalTokenCount": 15,
                    },
                },
                request=httpx.Request("POST", url),
            )
            return resp

        with (
            patch("app.services.agents.llm_client.GEMINI_API_KEY", "test"),
            patch("httpx.AsyncClient.post", side_effect=mock_post),
        ):
            from app.services.agents.llm_client import _call_gemini

            result = await _call_gemini("system", "user")

        assert result == {"test": "ok"}
        assert captured_json["generationConfig"]["responseMimeType"] == "application/json"
        assert captured_json["generationConfig"]["temperature"] == 0.3
