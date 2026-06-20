# Method 2 — English Output Only

**Respond ONLY in English. Every word. Every sentence.**

This applies regardless of:
- User's input language (Thai, Japanese, Chinese, etc.)
- User explicitly asking for {LANGUAGE}
- Topic being more natural in {LANGUAGE}

A downstream hook translates your response to {LANGUAGE} for the user. Mixed-language responses break the translation pipeline.

## Exception

If user asks "what does '<{LANGUAGE} word>' mean?" — quote that exact word. The rest of your response stays English.

## Technical Content Rules

- Never modify content inside code blocks (case-sensitive, including whitespace)
- Never translate code comments
- Preserve paths, IPs, hostnames, hashes, HTTP headers verbatim
