"""
TranslateGemma supported languages — 57 languages.
Codes follow ISO 639-1 (Alpha-2) with optional region codes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Language:
    code: str
    name: str


LANGUAGES: list[Language] = [
    Language("af", "Afrikaans"),
    Language("ar", "Arabic"),
    Language("bg", "Bulgarian"),
    Language("bn", "Bengali"),
    Language("ca", "Catalan"),
    Language("cs", "Czech"),
    Language("cy", "Welsh"),
    Language("da", "Danish"),
    Language("de", "German"),
    Language("el", "Greek"),
    Language("en", "English"),
    Language("es", "Spanish"),
    Language("et", "Estonian"),
    Language("fa", "Persian"),
    Language("fi", "Finnish"),
    Language("fr", "French"),
    Language("ga", "Irish"),
    Language("gd", "Scottish Gaelic"),
    Language("gl", "Galician"),
    Language("gu", "Gujarati"),
    Language("he", "Hebrew"),
    Language("hi", "Hindi"),
    Language("hr", "Croatian"),
    Language("hu", "Hungarian"),
    Language("id", "Indonesian"),
    Language("it", "Italian"),
    Language("ja", "Japanese"),
    Language("kn", "Kannada"),
    Language("ko", "Korean"),
    Language("lt", "Lithuanian"),
    Language("lv", "Latvian"),
    Language("mk", "Macedonian"),
    Language("ml", "Malayalam"),
    Language("mr", "Marathi"),
    Language("ms", "Malay"),
    Language("mt", "Maltese"),
    Language("nl", "Dutch"),
    Language("no", "Norwegian"),
    Language("pl", "Polish"),
    Language("pt", "Portuguese"),
    Language("ro", "Romanian"),
    Language("ru", "Russian"),
    Language("sk", "Slovak"),
    Language("sl", "Slovenian"),
    Language("sq", "Albanian"),
    Language("sr", "Serbian"),
    Language("sv", "Swedish"),
    Language("sw", "Swahili"),
    Language("ta", "Tamil"),
    Language("te", "Telugu"),
    Language("th", "Thai"),
    Language("tr", "Turkish"),
    Language("uk", "Ukrainian"),
    Language("ur", "Urdu"),
    Language("vi", "Vietnamese"),
    Language("zh", "Chinese (Simplified)"),
    Language("zh-Hant", "Chinese (Traditional)"),
]

_code_map: dict[str, Language] = {lang.code.lower(): lang for lang in LANGUAGES}
_name_map: dict[str, Language] = {lang.name.lower(): lang for lang in LANGUAGES}


def resolve_language(input_: str) -> Optional[Language]:
    """Resolve a language code or name to a Language object. Case-insensitive."""
    lower = input_.lower().replace("_", "-")
    return _code_map.get(lower) or _name_map.get(lower)


def is_supported(code: str) -> bool:
    """Check if a language code is supported."""
    return code.lower().replace("_", "-") in _code_map
