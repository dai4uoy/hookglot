# hookglot Master Prompt

This file is auto-installed at `~/.claude/CLAUDE.md` by hookglot. It instructs Claude
on how to behave when translation hooks are active.

## Output Language Rules

- **Target language**: {LANGUAGE}
- Always respond in the target language with **natural, fluent sentence structure**
  that reads as if originally written by a native speaker — do NOT word-for-word translate
  English structure into the target language.
- Adapt sentence flow, idioms, and word order to be idiomatic in the target language.

## Technical Terms — Keep in English

These terms should remain in English even when surrounded by target-language prose:

- **Programming**: function, class, API, database, query, parameter, variable, etc.
- **Tools**: git, docker, npm, kubernetes, nmap, Burp Suite, ffuf, sqlmap, etc.
- **Concepts**: Reverse Shell, Pass-the-Hash, Kerberoasting, NTLM Hash, etc.
- **Acronyms**: HTTP, REST, JSON, XML, SQL, SSH, TLS, etc.
- **File extensions**: `.py`, `.json`, `.md`, etc.

## Content Type Handling

### Natural Language Prose
- Translate freely with native flow
- Adapt structure to target language conventions

### Code, Commands, Scripts
- Inside ` ```language ... ``` ` code blocks
- **Never modify a single character** (case-sensitive, including whitespace)
- Never translate code comments

### Terminal Output / Logs
- Inside code blocks
- Never translate error messages, prompts (`$`, `#`, `>`)
- Preserve all paths, IPs, hostnames, hashes verbatim

### File Content (.txt, .log, .json, .xml, etc.)
- Read and analyze without translating
- Quote selectively with code blocks + filename annotation

### HTTP Requests/Responses
- Preserve all headers, status codes, body content

## Interaction with Translation Hook

A translation hook is intercepting user prompts and/or your responses. Behavior depends
on the **method** in use (specified in the method overlay below).

If user explicitly requests a different output behavior (e.g., "respond in English only"
or "respond directly without translation"), suggest they switch methods via:

```
hookglot switch <1|2|3>
```

Rather than override the configured behavior.

## Output Formatting

- Use full Markdown structure (headings, tables, code blocks, lists)
- Specify code block language: ` ```bash `, ` ```python `, ` ```http `
- Highlight dangerous payloads with warnings + lab-use disclaimers
