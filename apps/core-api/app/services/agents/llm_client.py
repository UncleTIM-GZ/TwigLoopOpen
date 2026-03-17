"""Platform LLM client — provider-neutral with Gemini + Anthropic backends.

Supports multiple providers via LLM_PROVIDER env var.
All calls are async with timeout, error handling, and transparent fallback.
"""

import json
import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)

# Provider config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini | anthropic
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "15"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))

# Gemini config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

# Anthropic config (fallback)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

PROMPT_VERSION = "v1.0"


async def generate_structured(
    system_prompt: str,
    user_prompt: str,
    *,
    agent_name: str = "",
    trace_id: str = "",
    task_id: str = "",
) -> dict | None:
    """Generate structured JSON from LLM. Returns None on any failure.

    Tries configured provider first. Provider-neutral interface.
    """
    start = time.monotonic()
    provider = LLM_PROVIDER
    failure_type = ""

    if provider == "gemini" and GEMINI_API_KEY:
        result = await _call_gemini(system_prompt, user_prompt)
    elif provider == "anthropic" and ANTHROPIC_API_KEY:
        result = await _call_anthropic(system_prompt, user_prompt)
    elif GEMINI_API_KEY:
        provider = "gemini"
        result = await _call_gemini(system_prompt, user_prompt)
    elif ANTHROPIC_API_KEY:
        provider = "anthropic"
        result = await _call_anthropic(system_prompt, user_prompt)
    else:
        logger.warning("No LLM API key configured")
        return None

    latency_ms = int((time.monotonic() - start) * 1000)
    if result is None:
        failure_type = "parse_or_api_failure"

    model = GEMINI_MODEL if provider == "gemini" else ANTHROPIC_MODEL

    # Record metrics
    from app.metrics import metrics

    metrics.inc("llm_calls_total", provider=provider, model=model)
    metrics.timing("llm_latency_ms", latency_ms, provider=provider)
    if result:
        metrics.inc("llm_calls_success", provider=provider)
    else:
        metrics.inc("llm_calls_failed", provider=provider, failure=failure_type)

    logger.info(
        "llm_call_completed",
        extra={
            "event_type": "llm_call_completed",
            "provider": provider,
            "model": model,
            "prompt_version": PROMPT_VERSION,
            "result_status": "success" if result else "failed",
            "failure_type": failure_type,
            "latency_ms": latency_ms,
            "agent_name": agent_name,
            "trace_id": trace_id,
            "task_id": task_id,
        },
    )
    return result


async def _call_gemini(system_prompt: str, user_prompt: str) -> dict | None:
    """Call Gemini API via Google AI Studio REST endpoint."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta"
        f"/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(
                url,
                headers={"content-type": "application/json"},
                json={
                    "systemInstruction": {
                        "parts": [{"text": system_prompt}],
                    },
                    "contents": [
                        {
                            "parts": [{"text": user_prompt}],
                        }
                    ],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "maxOutputTokens": LLM_MAX_TOKENS,
                        "temperature": 0.3,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

        # Log usage if available
        usage = data.get("usageMetadata", {})
        if usage:
            logger.info(
                "Gemini usage",
                extra={
                    "prompt_tokens": usage.get("promptTokenCount", 0),
                    "completion_tokens": usage.get("candidatesTokenCount", 0),
                    "total_tokens": usage.get("totalTokenCount", 0),
                },
            )

        # Extract text from Gemini response
        candidates = data.get("candidates", [])
        if not candidates:
            logger.warning("Gemini returned no candidates")
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None

        text = parts[0].get("text", "")
        return _parse_json_response(text)

    except httpx.TimeoutException:
        logger.warning("Gemini call timed out after %ds", LLM_TIMEOUT)
        return None
    except httpx.HTTPStatusError as e:
        logger.warning("Gemini API error: %s", e.response.status_code)
        return None
    except Exception:
        logger.exception("Unexpected Gemini client error")
        return None


async def _call_anthropic(system_prompt: str, user_prompt: str) -> dict | None:
    """Call Anthropic Claude API."""
    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": ANTHROPIC_MODEL,
                    "max_tokens": LLM_MAX_TOKENS,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
            response.raise_for_status()
            data = response.json()

        # Log usage if available
        usage = data.get("usage", {})
        if usage:
            logger.info(
                "Anthropic usage",
                extra={
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                },
            )

        content_blocks = data.get("content", [])
        if not content_blocks:
            return None

        text = content_blocks[0].get("text", "")
        return _parse_json_response(text)

    except httpx.TimeoutException:
        logger.warning("Anthropic call timed out after %ds", LLM_TIMEOUT)
        return None
    except httpx.HTTPStatusError as e:
        logger.warning("Anthropic API error: %s", e.response.status_code)
        return None
    except Exception:
        logger.exception("Unexpected Anthropic client error")
        return None


def _parse_json_response(text: str) -> dict | None:
    """Parse JSON from LLM response text. Handles markdown fencing."""
    if not text:
        return None

    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
        if not isinstance(result, dict):
            logger.warning("LLM response parsed but not a dict")
            return None
        return result
    except json.JSONDecodeError:
        logger.warning("LLM response not valid JSON")
        return None
