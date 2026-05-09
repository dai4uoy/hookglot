"""Configuration management for hookglot.

Config lives at ~/.hookglot/config.yaml
API keys live at ~/.hookglot/.env
"""
import os
import sys
import yaml
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".hookglot"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
ENV_FILE = CONFIG_DIR / ".env"

DEFAULT_CONFIG = {
    "version": 1,
    "language": "th",
    "method": 1,
    "translator": "ollama",
    "providers": {
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "qwen2.5:7b",
            "timeout": 60,
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "api_key_env": "OPENAI_API_KEY",
        },
        "anthropic": {
            "model": "claude-haiku-4-5",
            "api_key_env": "ANTHROPIC_API_KEY",
        },
        "google": {
            "model": "gemini-2.0-flash",
            "api_key_env": "GOOGLE_API_KEY",
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "api_key_env": "DEEPSEEK_API_KEY",
        },
        "alibaba": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-turbo",
            "api_key_env": "DASHSCOPE_API_KEY",
        },
        "moonshot": {
            "base_url": "https://api.moonshot.cn/v1",
            "model": "moonshot-v1-8k",
            "api_key_env": "MOONSHOT_API_KEY",
        },
        "zhipu": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4-flash",
            "api_key_env": "ZHIPU_API_KEY",
        },
        "nvidia": {
            "base_url": "https://integrate.api.nvidia.com/v1",
            "model": "meta/llama-3.1-70b-instruct",
            "api_key_env": "NVIDIA_API_KEY",
        },
    },
}


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_env():
    """Load API keys from ~/.hookglot/.env into os.environ."""
    if not ENV_FILE.exists():
        return
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


def load_config() -> dict:
    """Load config from ~/.hookglot/config.yaml. Returns defaults if missing."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
    except (yaml.YAMLError, OSError):
        return DEFAULT_CONFIG.copy()

    # Merge with defaults (user values override defaults)
    config = DEFAULT_CONFIG.copy()
    config.update({k: v for k, v in user_config.items() if k != "providers"})
    if "providers" in user_config:
        config["providers"] = {**DEFAULT_CONFIG["providers"], **user_config["providers"]}
    return config


def save_config(config: dict):
    """Save config to ~/.hookglot/config.yaml."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def get_provider_config(provider_name: str) -> dict:
    """Get config for specific provider."""
    config = load_config()
    if provider_name not in config["providers"]:
        raise ValueError(f"Unknown provider: {provider_name}")
    return config["providers"][provider_name]


def get_api_key(provider_name: str) -> Optional[str]:
    """Get API key for a provider from environment."""
    load_env()
    pconfig = get_provider_config(provider_name)
    env_var = pconfig.get("api_key_env")
    if not env_var:
        return None  # Ollama doesn't need a key
    return os.environ.get(env_var)


def write_env_file(keys: dict):
    """Write/update API keys in ~/.hookglot/.env."""
    ensure_config_dir()
    existing = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    existing[k.strip()] = v.strip()

    existing.update(keys)

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("# hookglot API keys — keep this file private!\n")
        for k, v in sorted(existing.items()):
            f.write(f"{k}={v}\n")

    # Set restrictive permissions on Unix-like systems.
    # Windows has no chmod equivalent; the file is in user's home dir
    # which is already access-restricted by the OS.
    if sys.platform != "win32":
        try:
            os.chmod(ENV_FILE, 0o600)
        except OSError:
            pass
