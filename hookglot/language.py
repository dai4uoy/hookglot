"""Language metadata for hookglot.

Defines supported Asian languages with their codes, native names,
and Unicode ranges for content-based detection.
"""
from dataclasses import dataclass


@dataclass
class Language:
    code: str
    english_name: str
    native_name: str
    unicode_ranges: list  # for content detection
    uses_latin: bool      # if True, can't reliably detect from Unicode alone


LANGUAGES = {
    "th": Language(
        code="th",
        english_name="Thai",
        native_name="ภาษาไทย",
        unicode_ranges=[(0x0E00, 0x0E7F)],
        uses_latin=False,
    ),
    "ja": Language(
        code="ja",
        english_name="Japanese",
        native_name="日本語",
        unicode_ranges=[(0x3040, 0x309F), (0x30A0, 0x30FF), (0x4E00, 0x9FFF)],
        uses_latin=False,
    ),
    "zh-CN": Language(
        code="zh-CN",
        english_name="Chinese (Simplified)",
        native_name="简体中文",
        unicode_ranges=[(0x4E00, 0x9FFF)],
        uses_latin=False,
    ),
    "zh-TW": Language(
        code="zh-TW",
        english_name="Chinese (Traditional)",
        native_name="繁體中文",
        unicode_ranges=[(0x4E00, 0x9FFF)],
        uses_latin=False,
    ),
    "ko": Language(
        code="ko",
        english_name="Korean",
        native_name="한국어",
        unicode_ranges=[(0xAC00, 0xD7AF), (0x1100, 0x11FF)],
        uses_latin=False,
    ),
    "vi": Language(
        code="vi",
        english_name="Vietnamese",
        native_name="Tiếng Việt",
        unicode_ranges=[],
        uses_latin=True,  # uses Latin with diacritics
    ),
    "id": Language(
        code="id",
        english_name="Indonesian",
        native_name="Bahasa Indonesia",
        unicode_ranges=[],
        uses_latin=True,
    ),
    "ms": Language(
        code="ms",
        english_name="Malay",
        native_name="Bahasa Melayu",
        unicode_ranges=[],
        uses_latin=True,
    ),
}


def has_target_language_chars(text: str, lang_code: str) -> bool:
    """Check if text contains characters from the target language.

    For Latin-based languages (Vietnamese, Indonesian, Malay), this always
    returns True since we can't distinguish them from English by Unicode alone.
    The hook will rely on user config in those cases.
    """
    if lang_code not in LANGUAGES:
        return False

    lang = LANGUAGES[lang_code]

    # Latin languages: assume the prompt is in target language if user configured it
    if lang.uses_latin:
        return True

    # Non-Latin: check Unicode ranges
    for char in text:
        cp = ord(char)
        for start, end in lang.unicode_ranges:
            if start <= cp <= end:
                return True
    return False


def get_language(code: str) -> Language:
    """Get language metadata by code."""
    if code not in LANGUAGES:
        raise ValueError(
            f"Unsupported language: {code}. "
            f"Supported: {', '.join(LANGUAGES.keys())}"
        )
    return LANGUAGES[code]
