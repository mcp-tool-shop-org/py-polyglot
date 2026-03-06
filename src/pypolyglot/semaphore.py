"""
Async counting semaphore for limiting concurrent Ollama calls.
Prevents GPU OOM on systems with limited VRAM.

Default concurrency: 1. Override with POLYGLOT_CONCURRENCY env var.
"""

from __future__ import annotations

import asyncio
import os
from typing import Callable, Optional

DEFAULT_CONCURRENCY = int(os.environ.get("POLYGLOT_CONCURRENCY", "1")) or 1


class Semaphore:
    """Async counting semaphore wrapping asyncio.Semaphore.

    Supports both context manager and manual acquire/release patterns::

        async with sem:
            ...

        release = await sem.acquire()
        try: ...
        finally: release()
    """

    def __init__(self, limit: int = DEFAULT_CONCURRENCY) -> None:
        if limit < 1:
            raise ValueError("Semaphore limit must be >= 1")
        self._limit = limit
        self._sem = asyncio.Semaphore(limit)
        self._lock = asyncio.Lock()
        self._active = 0

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def active(self) -> int:
        return self._active

    async def acquire(self) -> Callable[[], None]:
        """Acquire a permit. Returns a release function."""
        await self._sem.acquire()
        async with self._lock:
            self._active += 1
        return self._release

    def _release(self) -> None:
        self._active -= 1
        self._sem.release()

    async def __aenter__(self) -> Semaphore:
        await self._sem.acquire()
        async with self._lock:
            self._active += 1
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: object,
    ) -> None:
        self._active -= 1
        self._sem.release()


# Shared global semaphore for Ollama calls
ollama_semaphore = Semaphore(DEFAULT_CONCURRENCY)
