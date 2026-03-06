"""
Segment-level translation cache.

Hashes source text + target language + model to avoid re-translating
unchanged segments. Cache file lives alongside the source as .polyglot-cache.json.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Default cache TTL: 30 days in seconds
CACHE_TTL_S = 30 * 24 * 60 * 60

# Minimum similarity threshold for fuzzy cache hits (0-1)
FUZZY_THRESHOLD = 0.85


@dataclass
class CacheEntry:
    translation: str
    model: str
    timestamp: float
    source: Optional[str] = None
    target_lang: Optional[str] = None


@dataclass
class TranslationCache:
    version: int = 1
    entries: dict[str, CacheEntry] = field(default_factory=dict)


def cache_key(text: str, target_lang: str, model: str) -> str:
    """Generate a cache key from source text, target language, and model."""
    h = hashlib.sha256(f"{target_lang}:{model}:{text}".encode()).hexdigest()
    return h[:16]


def create_cache() -> TranslationCache:
    return TranslationCache()


def load_cache(readme_path: str) -> TranslationCache:
    """Load cache from disk. Returns empty cache if file doesn't exist or is invalid."""
    cache_path = _get_cache_path(readme_path)
    if not cache_path.exists():
        return create_cache()
    try:
        raw = json.loads(cache_path.read_text("utf-8"))
        if raw.get("version") == 1 and "entries" in raw:
            entries = {}
            for k, v in raw["entries"].items():
                entries[k] = CacheEntry(
                    translation=v["translation"],
                    model=v["model"],
                    timestamp=v["timestamp"],
                    source=v.get("source"),
                    target_lang=v.get("targetLang"),
                )
            return TranslationCache(version=1, entries=entries)
        return create_cache()
    except Exception:
        return create_cache()


def save_cache(readme_path: str, cache: TranslationCache) -> None:
    """Save cache to disk next to the README."""
    cache_path = _get_cache_path(readme_path)
    data = {
        "version": cache.version,
        "entries": {
            k: {
                "translation": v.translation,
                "model": v.model,
                "timestamp": v.timestamp,
                **({"source": v.source} if v.source else {}),
                **({"targetLang": v.target_lang} if v.target_lang else {}),
            }
            for k, v in cache.entries.items()
        },
    }
    cache_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), "utf-8")


def get_cached(
    cache: TranslationCache, key: str, ttl_s: float = CACHE_TTL_S
) -> Optional[str]:
    """Look up a cached translation. Returns None on miss or if expired."""
    entry = cache.entries.get(key)
    if entry is None:
        return None
    if time.time() - entry.timestamp > ttl_s:
        del cache.entries[key]
        return None
    return entry.translation


def prune_cache(cache: TranslationCache, ttl_s: float = CACHE_TTL_S) -> int:
    """Remove all expired entries. Returns number pruned."""
    now = time.time()
    expired = [k for k, v in cache.entries.items() if now - v.timestamp > ttl_s]
    for k in expired:
        del cache.entries[k]
    return len(expired)


def clear_cache(cache: TranslationCache) -> int:
    """Clear all entries. Returns number cleared."""
    count = len(cache.entries)
    cache.entries.clear()
    return count


def set_cached(
    cache: TranslationCache,
    key: str,
    translation: str,
    model: str,
    source: Optional[str] = None,
    target_lang: Optional[str] = None,
) -> None:
    """Store a translation in the cache."""
    cache.entries[key] = CacheEntry(
        translation=translation,
        model=model,
        timestamp=time.time(),
        source=source,
        target_lang=target_lang,
    )


# --- Fuzzy matching ---


def similarity(a: str, b: str) -> float:
    """Compute normalised similarity using Levenshtein distance.

    Returns a value between 0 (completely different) and 1 (identical).
    Uses iterative Wagner-Fischer with single-row optimisation.
    """
    if a == b:
        return 1.0
    a_n = a.lower()
    b_n = b.lower()
    if a_n == b_n:
        return 1.0

    m, n = len(a_n), len(b_n)
    if m == 0 or n == 0:
        return 0.0

    max_len = max(m, n)

    # Single-row Levenshtein
    prev = list(range(n + 1))
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            cost = 0 if a_n[i - 1] == b_n[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,       # deletion
                curr[j - 1] + 1,   # insertion
                prev[j - 1] + cost  # substitution
            )
        prev, curr = curr, prev

    return 1.0 - prev[n] / max_len


def get_fuzzy_cached(
    cache: TranslationCache,
    text: str,
    target_lang: str,
    model: str,
    ttl_s: float = CACHE_TTL_S,
    threshold: float = FUZZY_THRESHOLD,
) -> Optional[dict]:
    """Fuzzy cache lookup — finds the best cached entry above threshold.

    Returns {"translation": str, "similarity": float} or None.
    """
    now = time.time()
    best_sim = threshold
    best_translation: Optional[str] = None

    for entry in cache.entries.values():
        if not entry.source:
            continue
        if now - entry.timestamp > ttl_s:
            continue
        if entry.model != model:
            continue
        if entry.target_lang and entry.target_lang != target_lang:
            continue

        sim = similarity(text, entry.source)
        if sim > best_sim:
            best_sim = sim
            best_translation = entry.translation

    if best_translation is not None:
        return {"translation": best_translation, "similarity": best_sim}
    return None


def _get_cache_path(readme_path: str) -> Path:
    """Get the cache file path next to the source file."""
    dir_ = Path(readme_path).resolve().parent
    cache_path = (dir_ / ".polyglot-cache.json").resolve()
    # Guard against path traversal
    if not str(cache_path).startswith(str(dir_)):
        raise ValueError(f'Cache path traversal blocked: "{cache_path}" escapes "{dir_}".')
    return cache_path
