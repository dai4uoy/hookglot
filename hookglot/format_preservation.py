"""Format preservation system for hookglot.

Layer 1: Smart code block extraction (triple backtick + inline)
Layer 2: Aggressive element protection (URLs, IPs, emails, env vars, paths)
Layer 3: Strict translator prompt instructions

Strategy: extract elements that should NEVER be translated, replace each with a
unique numeric placeholder, send only the prose to the translator, then restore
elements verbatim into the translated output.

Placeholder format: ⟨⟨hg_a1_0⟩⟩, ⟨⟨hg_a1_1⟩⟩, ... — randomized prefix so no preserve pattern can
match the placeholder itself (avoids nested-replacement bugs and user prompt hijacks).
"""
import re
import uuid
from dataclasses import dataclass


# ─────────────────────────────────────────────
# Patterns to preserve (order matters: process longer/specific first)
# ─────────────────────────────────────────────
PRESERVE_PATTERNS = [
    # Layer 1: Code blocks (highest priority — extract whole)
    ("CODE",   re.compile(r"```[\s\S]*?```", re.MULTILINE)),
    ("INLINE", re.compile(r"`[^`\n]+`")),

    # Layer 2: Aggressive element protection
    ("URL",    re.compile(r"https?://[^\s\)\]>'\"]+")),
    ("EMAIL",  re.compile(r"\b[\w\.\-+]+@[\w\.\-]+\.\w+\b")),
    ("IPV4",   re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b")),
    ("ENVVAR", re.compile(r"\$\{?[A-Z_][A-Z0-9_]*\}?")),
    ("PATH",   re.compile(r"(?:/[\w\.\-]+){2,}/?")),       # /etc/passwd, /var/log/x
    ("HOMEPATH", re.compile(r"~/[\w\.\-/]+")),              # ~/.ssh/id_rsa
    ("HASH",   re.compile(r"\b[a-fA-F0-9]{32,}\b")),        # MD5, SHA1, SHA256
    # Constants:
    #  - With underscores: NTLM_HASH, AWS_SECRET_KEY
    #  - Long all-caps: NOPASSWD, READONLY (7+ chars to reduce false positives)
    ("CONST",   re.compile(r"\b[A-Z]{2,}(?:_[A-Z0-9]+)+\b")),
    ("ALLCAPS", re.compile(r"\b[A-Z]{7,}\b")),
]


@dataclass
class PreservedDoc:
    """A document with preserved elements extracted."""
    text: str           # text with placeholders
    preserved: dict     # placeholder -> original

    def restore(self, translated_text: str) -> str:
        """Restore placeholders in the translated text.

        Iterates placeholders in reverse numeric order so that any reference like
        ⟨⟨10⟩⟩ is replaced before ⟨⟨1⟩⟩.
        """
        result = translated_text

        def placeholder_index(p: str) -> int:
            try:
                # แก้ไขการอ่านเลข: ⟨⟨hg_a1_10⟩⟩ -> ตัดวงเล็บเหลือ hg_a1_10 -> แยกด้วย _ เอาตัวสุดท้าย -> 10
                return int(p.strip("⟨⟩").split("_")[-1])
            except (ValueError, IndexError):
                return -1

        for placeholder in sorted(self.preserved.keys(), key=placeholder_index, reverse=True):
            original = self.preserved[placeholder]
            result = result.replace(placeholder, original)

        return result


def preserve(text: str) -> PreservedDoc:
    """Extract preservable elements and replace with placeholders.

    Returns a PreservedDoc that can be used to restore originals later.
    """
    
    session_id = f"hg_{uuid.uuid4().hex[:2]}_"
    
    counter = [0]  # mutable holder for closure
    preserved = {}
    working = text

    for _pattern_name, pattern in PRESERVE_PATTERNS:
        def make_placeholder(match):
            placeholder = f"⟨⟨{session_id}{counter[0]}⟩⟩"
            preserved[placeholder] = match.group(0)
            counter[0] += 1
            return placeholder

        working = pattern.sub(make_placeholder, working)

    return PreservedDoc(text=working, preserved=preserved)


# ─────────────────────────────────────────────
# Layer 3: Translator system prompt
# ─────────────────────────────────────────────
TRANSLATOR_INSTRUCTION_TEMPLATE = """You are a precise translator from {source_lang} to {target_lang}.

CRITICAL RULES:
1. Preserve placeholders EXACTLY as they appear (e.g., ⟨⟨hg_a1_0⟩⟩, ⟨⟨hg_a1_1⟩⟩).
   - Do NOT translate them
   - Do NOT modify the brackets ⟨⟨ ⟩⟩
   - Do NOT change the characters or numbers inside
   - Pass them through unchanged in their original positions

2. Preserve Markdown syntax EXACTLY:
   - Headings: # ## ### #### ##### ######
   - Bold/italic: **bold** *italic* __bold__ _italic_
   - Lists: - * + 1. 2. 3.
   - Tables: | col | col |
   - Quotes: > text
   - Horizontal rules: ---

3. Preserve technical terms in English (do not translate):
   - Programming concepts (function, class, API, database, etc.)
   - Tool names (git, docker, npm, kubernetes, etc.)
   - File extensions (.py, .json, .md, etc.)
   - Acronyms (HTTP, REST, JSON, XML, SQL, etc.)

4. Translate ONLY the natural prose between markdown elements and placeholders.

5. Use natural, fluent {target_lang} sentence structure
   that reads as if originally written by a native speaker.
   Do NOT word-for-word translate — adapt the structure.

6. Preserve all line breaks and empty lines exactly.

OUTPUT: Only the translated text. No preamble. No explanation. No quotes."""


def get_translator_instruction(source_lang: str, target_lang: str) -> str:
    """Build the translator system prompt for a language pair."""
    return TRANSLATOR_INSTRUCTION_TEMPLATE.format(
        source_lang=source_lang,
        target_lang=target_lang,
    )