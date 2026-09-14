"""
EZChart — AI client wrapper.

Abstracts away the Gemini API call, so providers can be swapped
later (OpenAI, Claude, local model) without touching handlers.

Uses google-genai SDK with Gemini Flash models (free-tier friendly).

Key features:
- Auto-normalizes model name to "models/..." format required by SDK
- Fallback chain if primary model is unavailable
- Multilingual prompts (ru / en / it)
- Timeout protection (60s)
- Cleans accidental markdown fences from response
"""

import asyncio
from typing import Final

from google import genai
from google.genai import types as genai_types

from src.config import settings
from src.services.prompts import get_prompt
from src.utils.logger import get_logger

log = get_logger(__name__)

# Timeout for AI call (seconds)
AI_TIMEOUT: Final[int] = 60

# Fallback chain: if primary model fails with 404, try these in order
FALLBACK_MODELS: Final[tuple[str, ...]] = (
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-2.0-flash-001",  # last versioned release of 2.0
)

# Singleton client
_client: genai.Client | None = None


class AIClientError(Exception):
    """Raised when AI call fails for any reason."""


def _get_client() -> genai.Client:
    """Lazy-init Gemini client."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _normalize_model_name(name: str) -> str:
    """
    Ensure model name has the 'models/' prefix required by google-genai SDK.

    Also defensively strips common misconfigurations:
    - "GEMINI_MODEL=gemini-2.0-flash" → "gemini-2.0-flash"
    - "models/gemini-2.0-flash" → unchanged
    - "  gemini-2.0-flash  " → "models/gemini-2.0-flash"
    """
    name = name.strip()

    # Defensive: strip leading "GEMINI_MODEL=" or any "KEY=" prefix
    if "=" in name:
        name = name.split("=", 1)[1].strip()

    # Strip leading "models/" if present (we'll re-add it consistently)
    if name.startswith("models/"):
        name = name[len("models/"):]

    return f"models/{name}"


def _build_candidates() -> list[str]:
    """
    Build ordered list of model candidates to try:
    primary (from .env) first, then fallbacks.
    All normalized to 'models/...' format.
    """
    raw_candidates = [settings.gemini_model, *FALLBACK_MODELS]

    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for raw in raw_candidates:
        normalized = _normalize_model_name(raw)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _strip_code_fences(text: str) -> str:
    """Remove accidental ```markdown fences that Gemini sometimes adds."""
    if text.startswith("```"):
        # Drop opening fence line
        text = text.split("\n", 1)[-1] if "\n" in text else text
        # Drop closing fence
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
    return text


def _call_gemini_sync(model: str, image_bytes: bytes, prompt: str) -> str:
    """
    Synchronous Gemini call — will be run in a thread.

    Args:
        model: Fully-qualified model name (with "models/" prefix).
        image_bytes: JPEG bytes of the chart screenshot.
        prompt: Vision prompt in the desired language.

    Returns:
        Response text (with markdown fences stripped).

    Raises:
        AIClientError: on empty response.
    """
    client = _get_client()

    contents = [
        genai_types.Content(
            parts=[
                genai_types.Part(text=prompt),
                genai_types.Part(
                    inline_data=genai_types.Blob(
                        mime_type="image/jpeg",
                        data=image_bytes,
                    )
                ),
            ]
        )
    ]

    response = client.models.generate_content(
        model=model,
        contents=contents,
    )

    if not response or not response.text:
        raise AIClientError(f"Empty response from {model}")

    return _strip_code_fences(response.text.strip())


async def analyze_chart(image_bytes: bytes, locale: str = "en") -> str:
    """
    Send image to Gemini Vision, return structured analysis text.

    Tries primary model first; if 404 (model not found), falls back
    to alternatives. Other errors (403, 429, timeout) abort immediately.

    Args:
        image_bytes: JPEG bytes of the chart screenshot.
        locale: Language code for the response ("ru", "en", "it").
                Falls back to English for unsupported locales.

    Raises:
        AIClientError: on any failure (network, quota, bad response).
    """
    prompt = get_prompt(locale)
    candidates = _build_candidates()
    last_error: Exception | None = None

    for model in candidates:
        try:
            log.info(
                "ai_request",
                model=model,
                locale=locale,
                image_size=len(image_bytes),
            )

            result = await asyncio.wait_for(
                asyncio.to_thread(
                    _call_gemini_sync, model, image_bytes, prompt
                ),
                timeout=AI_TIMEOUT,
            )

            log.info("ai_response_ok", model=model, length=len(result))
            return result

        except asyncio.TimeoutError as e:
            log.warning("ai_timeout", model=model, timeout=AI_TIMEOUT)
            last_error = AIClientError(
                f"{model}: timed out after {AI_TIMEOUT}s"
            )
            raise last_error from e

        except Exception as e:
            err_str = str(e)
            is_model_unavailable = (
                "404" in err_str
                or "NOT_FOUND" in err_str
                or "no longer available" in err_str
                or "not found" in err_str.lower()
            )

            if is_model_unavailable:
                log.warning(
                    "ai_model_unavailable",
                    model=model,
                    error=err_str[:200],
                )
                last_error = e
                continue

            # Any other error (403, 429, 400 format) — abort immediately
            log.exception("ai_unexpected_error", model=model)
            raise AIClientError(f"AI call failed: {e}") from e

    # All candidates exhausted
    raise AIClientError(
        f"All Gemini models unavailable. Last error: {last_error}"
    )