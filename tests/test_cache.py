"""Tests for cache module."""

import time

from pypolyglot.cache import (
    cache_key,
    create_cache,
    get_cached,
    set_cached,
    prune_cache,
    clear_cache,
    similarity,
    get_fuzzy_cached,
)


def test_cache_key_deterministic():
    k1 = cache_key("hello", "ja", "model")
    k2 = cache_key("hello", "ja", "model")
    assert k1 == k2
    assert len(k1) == 16


def test_cache_key_varies():
    k1 = cache_key("hello", "ja", "model")
    k2 = cache_key("hello", "fr", "model")
    assert k1 != k2


def test_set_and_get():
    cache = create_cache()
    set_cached(cache, "k1", "translated", "model")
    assert get_cached(cache, "k1") == "translated"


def test_get_expired():
    cache = create_cache()
    set_cached(cache, "k1", "translated", "model")
    cache.entries["k1"].timestamp = time.time() - 100
    assert get_cached(cache, "k1", ttl_s=50) is None


def test_prune():
    cache = create_cache()
    set_cached(cache, "k1", "old", "model")
    cache.entries["k1"].timestamp = time.time() - 100
    set_cached(cache, "k2", "new", "model")
    pruned = prune_cache(cache, ttl_s=50)
    assert pruned == 1
    assert "k1" not in cache.entries
    assert "k2" in cache.entries


def test_clear():
    cache = create_cache()
    set_cached(cache, "k1", "a", "m")
    set_cached(cache, "k2", "b", "m")
    cleared = clear_cache(cache)
    assert cleared == 2
    assert len(cache.entries) == 0


def test_similarity_identical():
    assert similarity("hello", "hello") == 1.0


def test_similarity_case_insensitive():
    assert similarity("Hello", "hello") == 1.0


def test_similarity_different():
    sim = similarity("hello", "world")
    assert sim < 0.5


def test_similarity_similar():
    sim = similarity("Hello world", "Hello World!")
    assert sim > 0.8


def test_fuzzy_cache():
    cache = create_cache()
    set_cached(cache, "k1", "translated text", "model", source="Hello world", target_lang="ja")
    result = get_fuzzy_cached(cache, "Hello world!", "ja", "model")
    assert result is not None
    assert result["similarity"] > 0.85


def test_fuzzy_cache_no_match():
    cache = create_cache()
    set_cached(cache, "k1", "translated text", "model", source="Hello world", target_lang="ja")
    result = get_fuzzy_cached(cache, "Completely different text here", "ja", "model")
    assert result is None
