# Translation Providers

hookglot supports 9 translation providers. All except Ollama require an API key.

## Provider Overview

| Provider | Cost | Free Tier | Setup Difficulty | Best For |
|----------|------|-----------|------------------|----------|
| **Ollama** | Free | ✅ Always | ⭐ Easy | Privacy, offline |
| **OpenAI** | $0.15/1M | ❌ | ⭐ Easy | Reliable cloud option |
| **Anthropic** | $1/1M | ❌ | ⭐ Easy | High quality |
| **Google Gemini** | Free tier | ✅ Generous | ⭐ Easy | Free tier users |
| **DeepSeek** | $0.14/1M | ❌ | ⭐ Easy | Cheapest, Asian languages |
| **Alibaba** | $0.20/1M | ❌ | ⭐⭐ Medium | Chinese, Asian languages |
| **Moonshot** | $1/1M | ❌ | ⭐⭐ Medium (China) | Chinese language quality |
| **Zhipu AI** | Free tier | ✅ GLM-4 Flash | ⭐⭐ Medium (China) | Free GLM-4 Flash |
| **NVIDIA** | Free credits | ✅ | ⭐⭐ Medium | Multi-model gateway |

---

## Setup Instructions

### Ollama (Recommended for privacy)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended model
ollama pull qwen2.5:7b

# Switch hookglot to use it
hookglot translator ollama
```

No API key needed.

### OpenAI

1. Get key at https://platform.openai.com/api-keys
2. `hookglot translator openai`
3. `hookglot set-key openai`

### Anthropic

1. Get key at https://console.anthropic.com/settings/keys
2. `hookglot translator anthropic`
3. `hookglot set-key anthropic`

### Google Gemini

1. Get key at https://aistudio.google.com/apikey
2. `hookglot translator google`
3. `hookglot set-key google`

Free tier: 1500 requests/day for Gemini 2.0 Flash.

### DeepSeek

1. Get key at https://platform.deepseek.com/api_keys
2. `hookglot translator deepseek`
3. `hookglot set-key deepseek`

Best value for money — $0.14 per 1M tokens.

### Alibaba (DashScope)

1. Get key at https://dashscope.console.aliyun.com/apiKey
2. `hookglot translator alibaba`
3. `hookglot set-key alibaba`

### Moonshot

1. Get key at https://platform.moonshot.cn/console/api-keys
2. `hookglot translator moonshot`
3. `hookglot set-key moonshot`

⚠️ May require VPN if outside China.

### Zhipu AI

1. Get key at https://open.bigmodel.cn/usercenter/apikeys
2. `hookglot translator zhipu`
3. `hookglot set-key zhipu`

GLM-4 Flash is free.

### NVIDIA

1. Get key at https://build.nvidia.com/explore/discover (sign in)
2. `hookglot translator nvidia`
3. `hookglot set-key nvidia`

Free credit included.

---

## Changing Models

Edit `~/.hookglot/config.yaml` to change the model used by a provider:

```yaml
providers:
  ollama:
    model: qwen2.5:14b   # bigger = better quality, more RAM
  openai:
    model: gpt-4o-mini   # or gpt-4o for higher quality
  deepseek:
    model: deepseek-chat
```

---

## API Key Storage

Keys are stored in `~/.hookglot/.env` with `chmod 600` (only readable by you).

Never commit this file to git. Never share it with anyone.
