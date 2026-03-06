"""
Async counting semaphore for limiting concurrent Ollama calls.
Prevents GPU OOM on systems with limited VRAM.

Default concurrency: 1. Override with POLYGLOT_CONCURRENCY env var.
"""

from __future__ import annotations

import asyncio
import os

DEFAULT_CONCURRENCY = int(os.environ.get("POLYGLOT_CONCURRENCY", "1")) or 1


class Semaphore:
    """Async counting semaphore wrapping asyncio.Semaphore."""

    def __init__(self, limit: int = DEFAULT_CONCURRENCY):
        if limit < 1:
            raise ValueError("Semaphore limit must be >= 1")
        self._limit = limit
        self._sem = asyncio.Semaphore(limit)
        self._active = 0

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def active(self) -> int:
        return self._active

    async def acquire(self):
        """Acquire a permit. Returns an async context manager release function."""
        await self._sem.acquire()
        self._active += 1
        return self._release

    def _release(self) -> None:
        self._active -= 1
        self._sem.release()


# Shared global semaphore for Ollama calls
ollama_semaphore = Semaphore(DEFAULT_CONCURRENCY)
