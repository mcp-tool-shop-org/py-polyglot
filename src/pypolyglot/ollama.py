"""
Minimal Ollama HTTP client — uses httpx for async HTTP.
Auto-starts Ollama and auto-pulls models when needed.
"""

from __future__ import annotations

import asyncio
import json
import logging
import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable, Optional

import httpx

from .errors import ErrorCode, PolyglotError
from .semaphore import ollama_semaphore

logger = logging.getLogger(__name__)

# Timeouts
GENERATE_TIMEOUT_S = 60.0
API_TIMEOUT_S = 10.0
PULL_TIMEOUT_S = 600.0
STREAM_READ_TIMEOUT_S = 120.0  # per-chunk read timeout for streaming pulls

# Retry config
MAX_RETRIES = 2
RETRY_BASE_DELAY_S = 1.0


@dataclass
class OllamaGenerateRequest:
    model: str
    prompt: str
    stream: bool = False
    temperature: Optional[float] = None
    num_predict: Optional[int] = None
    top_p: Optional[float] = None


@dataclass
class OllamaGenerateResponse:
    model: str
    response: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


@dataclass
class OllamaModel:
    name: str
    size: int
    digest: str


StreamCallback = Callable[[str], None]


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self, timeout: float = GENERATE_TIMEOUT_S) -> httpx.AsyncClient:
        """Get or create the shared httpx client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(timeout, connect=10.0),
            )
        return self._client

    async def aclose(self) -> None:
        """Close the underlying httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def generate(self, req: OllamaGenerateRequest) -> OllamaGenerateResponse:
        """Generate a completion with automatic retry. Guarded by semaphore."""
        async with ollama_semaphore:
            return await self._generate_with_retry(req)

    async def _generate_with_retry(self, req: OllamaGenerateRequest) -> OllamaGenerateResponse:
        last_error: Optional[PolyglotError] = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                return await self._generate(req)
            except PolyglotError as err:
                if err.retryable and attempt < MAX_RETRIES:
                    last_error = err
                    delay = RETRY_BASE_DELAY_S * (2 ** attempt)
                    logger.warning(
                        "Retryable error (%s), retrying in %ss (attempt %d/%d)...",
                        err.code.value, delay, attempt + 1, MAX_RETRIES,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise
        raise last_error  # type: ignore[misc]

    async def _generate(self, req: OllamaGenerateRequest) -> OllamaGenerateResponse:
        body: dict = {"model": req.model, "prompt": req.prompt, "stream": False}
        options: dict = {}
        if req.temperature is not None:
            options["temperature"] = req.temperature
        if req.num_predict is not None:
            options["num_predict"] = req.num_predict
        if req.top_p is not None:
            options["top_p"] = req.top_p
        if options:
            body["options"] = options

        client = await self._get_client(GENERATE_TIMEOUT_S)
        try:
            resp = await client.post("/api/generate", json=body)
        except httpx.TimeoutException:
            raise PolyglotError(
                code=ErrorCode.OLLAMA_TIMEOUT,
                message=f"Ollama generate timed out after {GENERATE_TIMEOUT_S}s (model: {req.model}).",
                hint='Restart Ollama, reduce parallelism, or use a smaller model (translategemma:4b).',
                retryable=True,
            )
        except httpx.ConnectError:
            raise PolyglotError(
                code=ErrorCode.OLLAMA_UNAVAILABLE,
                message="Cannot connect to Ollama.",
                hint="Is it running? Start with: ollama serve",
                retryable=True,
            )
        except httpx.HTTPError as exc:
            raise PolyglotError(
                code=ErrorCode.NETWORK_ERROR,
                message="Network error reaching Ollama.",
                hint="Check that Ollama is running and responsive.",
                cause=exc,
                retryable=True,
            )

        if resp.status_code == 404 and "not found" in resp.text:
            raise PolyglotError(
                code=ErrorCode.MODEL_NOT_FOUND,
                message=f'Model "{req.model}" not found.',
                hint=f"Pull it with: ollama pull {req.model}",
                retryable=False,
            )
        if resp.status_code >= 400:
            raise PolyglotError(
                code=ErrorCode.OLLAMA_ERROR,
                message=f"Ollama error (HTTP {resp.status_code}, model: {req.model}).",
                hint=resp.text[:200],
                retryable=resp.status_code >= 500,
            )

        data = resp.json()
        return OllamaGenerateResponse(
            model=data.get("model", req.model),
            response=data.get("response", ""),
            done=data.get("done", True),
            total_duration=data.get("total_duration"),
            load_duration=data.get("load_duration"),
            eval_count=data.get("eval_count"),
            eval_duration=data.get("eval_duration"),
        )

    async def generate_stream(
        self, req: OllamaGenerateRequest, on_token: StreamCallback
    ) -> OllamaGenerateResponse:
        """Generate with streaming — yields tokens via on_token callback. Guarded by semaphore."""
        async with ollama_semaphore:
            return await self._generate_stream_with_retry(req, on_token)

    async def _generate_stream_with_retry(
        self, req: OllamaGenerateRequest, on_token: StreamCallback
    ) -> OllamaGenerateResponse:
        last_error: Optional[PolyglotError] = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                return await self._generate_stream(req, on_token)
            except PolyglotError as err:
                if err.retryable and attempt < MAX_RETRIES:
                    last_error = err
                    delay = RETRY_BASE_DELAY_S * (2 ** attempt)
                    logger.warning(
                        "Retryable error (%s), retrying in %ss (attempt %d/%d)...",
                        err.code.value, delay, attempt + 1, MAX_RETRIES,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise
        raise last_error  # type: ignore[misc]

    async def _generate_stream(
        self, req: OllamaGenerateRequest, on_token: StreamCallback
    ) -> OllamaGenerateResponse:
        body: dict = {"model": req.model, "prompt": req.prompt, "stream": True}
        options: dict = {}
        if req.temperature is not None:
            options["temperature"] = req.temperature
        if req.num_predict is not None:
            options["num_predict"] = req.num_predict
        if req.top_p is not None:
            options["top_p"] = req.top_p
        if options:
            body["options"] = options

        full_response = ""
        last_chunk: Optional[OllamaGenerateResponse] = None

        # Use a dedicated client for streaming with appropriate read timeout
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(GENERATE_TIMEOUT_S, connect=10.0, read=STREAM_READ_TIMEOUT_S),
        ) as stream_client:
            try:
                async with stream_client.stream("POST", "/api/generate", json=body) as resp:
                    if resp.status_code == 404:
                        await resp.aread()
                        if "not found" in resp.text:
                            raise PolyglotError(
                                code=ErrorCode.MODEL_NOT_FOUND,
                                message=f'Model "{req.model}" not found.',
                                hint=f"Pull it with: ollama pull {req.model}",
                                retryable=False,
                            )
                    if resp.status_code >= 400:
                        await resp.aread()
                        raise PolyglotError(
                            code=ErrorCode.OLLAMA_ERROR,
                            message=f"Ollama error (HTTP {resp.status_code}, model: {req.model}).",
                            hint=resp.text[:200],
                            retryable=resp.status_code >= 500,
                        )

                    buf = ""
                    async for chunk in resp.aiter_text():
                        buf += chunk
                        while "\n" in buf:
                            line, buf = buf.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                data = json.loads(line)
                                token = data.get("response", "")
                                if token:
                                    full_response += token
                                    on_token(token)
                                if data.get("done"):
                                    last_chunk = OllamaGenerateResponse(
                                        model=data.get("model", req.model),
                                        response=full_response,
                                        done=True,
                                        total_duration=data.get("total_duration"),
                                        load_duration=data.get("load_duration"),
                                        eval_count=data.get("eval_count"),
                                        eval_duration=data.get("eval_duration"),
                                    )
                            except (json.JSONDecodeError, KeyError) as exc:
                                logger.debug("Ignoring malformed stream chunk: %s", exc)
            except httpx.TimeoutException:
                raise PolyglotError(
                    code=ErrorCode.OLLAMA_TIMEOUT,
                    message=f"Ollama generate timed out after {GENERATE_TIMEOUT_S}s (model: {req.model}).",
                    hint='Restart Ollama, reduce parallelism, or use a smaller model (translategemma:4b).',
                    retryable=True,
                )
            except httpx.ConnectError:
                raise PolyglotError(
                    code=ErrorCode.OLLAMA_UNAVAILABLE,
                    message="Cannot connect to Ollama.",
                    hint="Is it running? Start with: ollama serve",
                    retryable=True,
                )
            except PolyglotError:
                raise
            except httpx.HTTPError as exc:
                raise PolyglotError(
                    code=ErrorCode.NETWORK_ERROR,
                    message="Network error reaching Ollama.",
                    hint="Check that Ollama is running and responsive.",
                    cause=exc,
                    retryable=True,
                )

        return last_chunk or OllamaGenerateResponse(
            model=req.model, response=full_response, done=True
        )

    async def list_models(self) -> list[OllamaModel]:
        client = await self._get_client(API_TIMEOUT_S)
        resp = await client.get("/api/tags")
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama list failed ({resp.status_code})")
        data = resp.json()
        return [
            OllamaModel(name=m["name"], size=m.get("size", 0), digest=m.get("digest", ""))
            for m in data.get("models", [])
        ]

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=3.0
            ) as client:
                resp = await client.get("/api/tags")
                return resp.status_code == 200
        except (OSError, httpx.HTTPError):
            return False

    async def has_model(self, name: str) -> bool:
        models = await self.list_models()
        return any(m.name == name or m.name.startswith(f"{name}:") for m in models)

    async def ensure_running(self) -> bool:
        """Start Ollama if not already running. Returns True if it became available."""
        if await self.is_available():
            return True

        ollama_path = "ollama"
        if platform.system() == "Windows":
            local_app = subprocess.os.environ.get("LOCALAPPDATA", "")
            candidates = [
                f"{local_app}\\Programs\\Ollama\\ollama.exe",
                f"{local_app}\\Ollama\\ollama.exe",
                "ollama",
            ]
            for c in candidates:
                if shutil.which(c) or _try_command(c):
                    ollama_path = c
                    break

        try:
            kwargs: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            if platform.system() == "Windows":
                kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwargs["start_new_session"] = True
            subprocess.Popen([ollama_path, "serve"], **kwargs)
        except OSError:
            return False

        for _ in range(20):
            await asyncio.sleep(0.5)
            if await self.is_available():
                return True
        return False

    async def ensure_model(self, name: str) -> bool:
        """Pull a model if not already present."""
        if await self.has_model(name):
            return True

        logger.info("Pulling %s (may be several GB)...", name)
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(PULL_TIMEOUT_S, connect=10.0, read=STREAM_READ_TIMEOUT_S),
            ) as pull_client:
                async with pull_client.stream(
                    "POST",
                    "/api/pull",
                    json={"name": name, "stream": True},
                ) as resp:
                    if resp.status_code != 200:
                        await resp.aread()
                        logger.error("Pull failed: %s", resp.text)
                        return False

                    last_pct = -1
                    buf = ""
                    async for chunk in resp.aiter_text():
                        buf += chunk
                        while "\n" in buf:
                            line, buf = buf.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                msg = json.loads(line)
                                total = msg.get("total", 0)
                                completed = msg.get("completed", 0)
                                if total and completed:
                                    pct = int(completed / total * 100)
                                    if pct != last_pct and pct % 10 == 0:
                                        logger.info("  %s: %d%%", msg.get("status", "downloading"), pct)
                                        last_pct = pct
                                elif msg.get("status") and msg["status"] != "pulling":
                                    logger.info("  %s", msg["status"])
                            except (json.JSONDecodeError, KeyError):
                                pass

            logger.info("%s ready.", name)
            return True
        except httpx.TimeoutException:
            logger.error("Pull timed out after %ss. Try: ollama pull %s", PULL_TIMEOUT_S, name)
            return False
        except (OSError, httpx.HTTPError) as exc:
            logger.error("Pull error: %s", exc)
            return False


def _try_command(cmd: str) -> bool:
    """Try running a command to see if it exists."""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
        return True
    except OSError:
        return False
