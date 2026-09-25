"""Inference backends. Every option here is free, and the default is local.

Provider picks, in the order ``auto`` tries them:

1. ``ollama``      — local Ollama (http://localhost:11434). No key, no quota,
                     no bill, works offline. The guaranteed-free path. Ollama is
                     already installed on this machine with several models.
2. ``gemini``      — Google AI Studio free tier (``GEMINI_API_KEY``).
3. ``groq``        — Groq free tier (``GROQ_API_KEY``).
4. ``openrouter``  — OpenRouter ``:free`` models (``OPENROUTER_API_KEY``).
5. ``template``    — no model at all: a deterministic outline built from the
                     brief, the retrieved corpus examples and real repo files.
                     Used for testing the pipeline and for offline CI.

Everything goes through ``urllib`` from the standard library, so there is
nothing to install and nothing to pay for.

Note on GitHub Models: it was retired on 2026-07-30, so BlogForge does not
offer it. The free CI path installs Ollama on the runner instead — see
``.github/workflows/blogforge.yml``.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from . import site

__all__ = [
    "ProviderError",
    "LLMResponse",
    "chat",
    "available_providers",
    "resolve_provider",
    "PROVIDERS",
]


class ProviderError(RuntimeError):
    """Raised when a backend cannot be used, with an actionable message."""


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    usage: dict = field(default_factory=dict)


#: provider -> env vars, default base URL, whether an API key is required
PROVIDERS: dict[str, dict[str, Any]] = {
    "ollama": {
        "env": ("OLLAMA_HOST",),
        "base": "http://localhost:11434",
        "needs_key": False,
        "hint": "Install from https://ollama.com, run `ollama serve`, then `ollama pull <model>`.",
    },
    "gemini": {
        "env": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        "base": "https://generativelanguage.googleapis.com/v1beta",
        "needs_key": True,
        "hint": "Get a free key at https://aistudio.google.com/apikey and export GEMINI_API_KEY.",
    },
    "groq": {
        "env": ("GROQ_API_KEY",),
        "base": "https://api.groq.com/openai/v1",
        "needs_key": True,
        "hint": "Get a free key at https://console.groq.com/keys and export GROQ_API_KEY.",
    },
    "openrouter": {
        "env": ("OPENROUTER_API_KEY",),
        "base": "https://openrouter.ai/api/v1",
        "needs_key": True,
        "hint": "Get a free key at https://openrouter.ai/keys and pick a model id ending in ':free'.",
    },
    "template": {
        "env": (),
        "base": "",
        "needs_key": False,
        "hint": "No model needed — produces a structure-only outline.",
    },
}

#: Model ids move fast. These are the defaults as of September 2026; override
#: with --model or the `model:` key in blogforge.yml. The local Ollama model is
#: the one that cannot be taken away from you.
DEFAULT_MODEL = site.DEFAULT_MODELS

_TIMEOUT = 900


def _env_key(provider: str) -> str:
    for name in PROVIDERS[provider]["env"]:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def _ollama_host(overrides: dict | None = None) -> str:
    overrides = overrides or {}
    host = (
        overrides.get("ollama_host")
        or os.environ.get("OLLAMA_HOST")
        or PROVIDERS["ollama"]["base"]
    )
    return host.rstrip("/")


def _ollama_alive(overrides: dict | None = None) -> bool:
    try:
        with urllib.request.urlopen(f"{_ollama_host(overrides)}/api/tags", timeout=3) as response:
            return response.status == 200
    except Exception:  # noqa: BLE001 - any failure simply means "not usable"
        return False


def resolve_provider(
    requested: str | None,
    model: str | None = None,
    overrides: dict | None = None,
) -> tuple[str, str]:
    """Pick a usable provider and model, honouring an explicit request."""
    if requested and requested != "auto":
        if requested not in PROVIDERS:
            raise ProviderError(
                f"unknown provider {requested!r}. Choose one of: {', '.join(PROVIDERS)}"
            )
        info = PROVIDERS[requested]
        if info["needs_key"] and not _env_key(requested):
            raise ProviderError(
                f"{requested} needs an API key in {' or '.join(info['env'])}. {info['hint']}"
            )
        if requested == "ollama" and not _ollama_alive(overrides):
            raise ProviderError(
                f"Ollama is not answering at {_ollama_host(overrides)}. {info['hint']}"
            )
        return requested, model or DEFAULT_MODEL[requested]

    for candidate in ("ollama", "gemini", "groq", "openrouter"):
        info = PROVIDERS[candidate]
        if info["needs_key"] and not _env_key(candidate):
            continue
        if candidate == "ollama" and not _ollama_alive(overrides):
            continue
        return candidate, model or DEFAULT_MODEL[candidate]
    return "template", model or "outline"


def available_providers(overrides: dict | None = None) -> list[dict[str, Any]]:
    """Introspection data for ``blogforge providers``."""
    out: list[dict[str, Any]] = []
    for name, info in PROVIDERS.items():
        if name == "ollama":
            ready = _ollama_alive(overrides)
            detail = "running" if ready else "not running"
        elif name == "template":
            ready, detail = True, "always available"
        else:
            key = _env_key(name)
            ready = bool(key)
            detail = "key set" if key else f"needs {'/'.join(info['env'])}"
        out.append(
            {
                "provider": name,
                "ready": ready,
                "detail": detail,
                "default_model": DEFAULT_MODEL[name],
                "base": info["base"],
                "hint": info["hint"],
            }
        )
    return out


def _post_json(url: str, payload: dict, headers: dict, timeout: int = _TIMEOUT) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:600]
        hint = {
            401: "the API key was rejected — check the environment variable",
            403: "the key is valid but not allowed to use this model",
            404: "model name not found — list the provider's models and pass --model",
            429: "free-tier rate limit hit — retry later, or use --provider ollama",
        }.get(exc.code, "check the provider status page")
        raise ProviderError(f"HTTP {exc.code} from {url}\n{detail}\nhint: {hint}") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(
            f"cannot reach {url} ({exc.reason}). For local Ollama, start it with `ollama serve`."
        ) from exc


def chat(
    messages: list[dict[str, str]],
    provider: str,
    model: str,
    temperature: float = 0.75,
    max_tokens: int = 8000,
    overrides: dict | None = None,
) -> LLMResponse:
    """Send a chat request to the chosen backend and return the generated text."""
    if provider == "ollama":
        return _chat_ollama(messages, model, temperature, max_tokens, overrides)
    if provider == "gemini":
        return _chat_gemini(messages, model, temperature, max_tokens, overrides)
    if provider in ("groq", "openrouter"):
        return _chat_openai_compatible(provider, messages, model, temperature, max_tokens, overrides)
    raise ProviderError(f"provider {provider!r} cannot generate text")


# --- adapters ------------------------------------------------------------------


def _chat_ollama(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    overrides: dict | None,
) -> LLMResponse:
    overrides = overrides or {}
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        # Thinking models (qwen3.5, deepseek-r1, ...) otherwise spend the whole
        # token budget inside message.thinking and return empty prose. Set
        # `ollama_think: true` in blogforge.yml to let them reason first.
        "think": bool(overrides.get("ollama_think", False)),
        "options": {"temperature": temperature, "num_ctx": 16384, "num_predict": max_tokens},
    }
    data = _post_json(f"{_ollama_host(overrides)}/api/chat", payload, {})
    message = data.get("message") or {}
    text = (message.get("content") or "").strip()
    thinking = (message.get("thinking") or "").strip()
    if not text:
        if thinking:
            raise ProviderError(
                f"{model} is a reasoning model and used the entire token budget on its "
                f"thinking ({len(thinking)} characters) before writing anything.\n"
                "hint: BlogForge already sends think=false — if you set ollama_think: true, "
                "turn it back off, raise max tokens, or use a non-reasoning model "
                "(e.g. --model qwen2.5-coder:7b)."
            )
        raise ProviderError(
            f"Ollama returned an empty response (done_reason={data.get('done_reason')!r}): "
            f"{json.dumps(data)[:400]}"
        )
    usage = {
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "completion_tokens": data.get("eval_count", 0),
    }
    return LLMResponse(text=text, provider="ollama", model=model, usage=usage)


def _chat_openai_compatible(
    provider: str,
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    overrides: dict | None,
) -> LLMResponse:
    base = (overrides or {}).get(f"{provider}_base") or PROVIDERS[provider]["base"]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {_env_key(provider)}"}
    if provider == "openrouter":
        # OpenRouter asks for an attribution header; harmless elsewhere.
        headers["HTTP-Referer"] = site.site_meta()["base_url"]
        headers["X-Title"] = "BlogForge"
    data = _post_json(f"{base.rstrip('/')}/chat/completions", payload, headers)
    choices = data.get("choices") or []
    text = ((choices[0].get("message") or {}).get("content") or "").strip() if choices else ""
    if not text:
        raise ProviderError(f"{provider} returned no text: {json.dumps(data)[:400]}")
    return LLMResponse(text=text, provider=provider, model=model, usage=data.get("usage") or {})


def _chat_gemini(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    overrides: dict | None,
) -> LLMResponse:
    base = (overrides or {}).get("gemini_base") or PROVIDERS["gemini"]["base"]
    system_parts = [m["content"] for m in messages if m.get("role") == "system"]
    contents = [
        {
            "role": "user" if m.get("role") != "assistant" else "model",
            "parts": [{"text": m.get("content", "")}],
        }
        for m in messages
        if m.get("role") != "system"
    ]
    payload: dict = {
        "contents": contents,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    if system_parts:
        payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
    url = f"{base.rstrip('/')}/models/{model}:generateContent?key={_env_key('gemini')}"
    data = _post_json(url, payload, {})
    candidates = data.get("candidates") or []
    parts = ((candidates[0].get("content") or {}).get("parts") or []) if candidates else []
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise ProviderError(f"gemini returned no text: {json.dumps(data)[:400]}")
    return LLMResponse(text=text, provider="gemini", model=model, usage=data.get("usageMetadata") or {})


