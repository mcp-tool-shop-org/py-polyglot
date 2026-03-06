"""
Glossary system — domain-specific term overrides for TranslateGemma.

Injects glossary hints into the prompt so the model uses the correct
translation for ambiguous terms.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GlossaryEntry:
    """A glossary entry with term and per-language translations."""
    term: str
    translations: dict[str, str] = field(default_factory=dict)


SOFTWARE_GLOSSARY: list[GlossaryEntry] = [
    GlossaryEntry("Architecture", {"ja": "アーキテクチャ", "zh": "架构", "ko": "아키텍처", "hi": "आर्किटेक्चर", "ar": "بنية النظام"}),
    GlossaryEntry("Adoption", {"ja": "導入", "zh": "采用", "ko": "도입", "hi": "अपनाना", "fr": "adoption (du produit)", "de": "Einführung"}),
    GlossaryEntry("Pipeline", {"ja": "パイプライン", "zh": "流水线", "ko": "파이프라인"}),
    GlossaryEntry("Deploy", {"ja": "デプロイ", "zh": "部署", "ko": "배포"}),
    GlossaryEntry("Library", {"ja": "ライブラリ", "zh": "库", "ko": "라이브러리"}),
    GlossaryEntry("Framework", {"ja": "フレームワーク", "zh": "框架", "ko": "프레임워크"}),
    GlossaryEntry("Build", {"ja": "ビルド", "zh": "构建", "ko": "빌드"}),
    GlossaryEntry("Release", {"ja": "リリース", "zh": "发布", "ko": "릴리스"}),
    GlossaryEntry("Branch", {"ja": "ブランチ", "zh": "分支", "ko": "브랜치"}),
    GlossaryEntry("Repository", {"ja": "リポジトリ", "zh": "仓库", "ko": "리포지토리"}),
    GlossaryEntry("Merge", {"ja": "マージ", "zh": "合并", "ko": "병합"}),
    GlossaryEntry("Token", {"ja": "トークン", "zh": "令牌", "ko": "토큰"}),
]


def build_glossary_hint(
    text: str,
    target_lang: str,
    glossary: list[GlossaryEntry],
) -> str:
    """Build a glossary hint string for the prompt.

    Only includes entries that have a translation for the target language
    AND where the term appears in the source text.
    """
    hints: list[str] = []
    text_lower = text.lower()
    lang_base = target_lang.split("-")[0].lower()

    for entry in glossary:
        if entry.term.lower() not in text_lower:
            continue
        translation = entry.translations.get(lang_base) or entry.translations.get(target_lang)
        if not translation:
            continue
        hints.append(f'"{entry.term}" → "{translation}"')

    if not hints:
        return ""
    return "\nIMPORTANT: Use these specific translations for the following terms:\n" + "\n".join(hints) + "\n"
