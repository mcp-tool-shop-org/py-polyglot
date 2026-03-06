"""Tests for the semaphore module."""

import asyncio

import pytest

from pypolyglot.semaphore import Semaphore


def test_semaphore_init():
    sem = Semaphore(3)
    assert sem.limit == 3
    assert sem.active == 0


def test_semaphore_invalid_limit():
    with pytest.raises(ValueError):
        Semaphore(0)
    with pytest.raises(ValueError):
        Semaphore(-1)


@pytest.mark.asyncio
async def test_acquire_release():
    sem = Semaphore(2)
    release = await sem.acquire()
    assert sem.active == 1
    release()
    assert sem.active == 0


@pytest.mark.asyncio
async def test_context_manager():
    sem = Semaphore(2)
    async with sem:
        assert sem.active == 1
    assert sem.active == 0


@pytest.mark.asyncio
async def test_context_manager_exception():
    """Semaphore releases even when body raises."""
    sem = Semaphore(1)
    with pytest.raises(ValueError):
        async with sem:
            assert sem.active == 1
            raise ValueError("boom")
    assert sem.active == 0


@pytest.mark.asyncio
async def test_concurrency_limit():
    """Semaphore blocks when limit is reached."""
    sem = Semaphore(1)
    entered = asyncio.Event()
    can_exit = asyncio.Event()

    async def hold():
        async with sem:
            entered.set()
            await can_exit.wait()

    async def try_enter():
        async with sem:
            return True

    task1 = asyncio.create_task(hold())
    await entered.wait()
    assert sem.active == 1

    # Start a second task — it should block
    task2 = asyncio.create_task(try_enter())
    await asyncio.sleep(0.05)
    assert sem.active == 1  # still 1, task2 is waiting

    # Release task1
    can_exit.set()
    result = await task2
    assert result is True
    assert sem.active == 0
    await task1
