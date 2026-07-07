import json
import os
from pathlib import Path

APP_NAME = "indextts"

CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG: dict = {
    "providers": {
        "gitee": {
            "base_url": "https://ai.gitee.com/v1",
        },
        "astraflow": {
            "base_url": "https://api.modelverse.cn/v1",
        },
    },
}

ENV_KEY_MAP = {
    "gitee": "GITEE_AI_API_KEY",
    "astraflow": "MODELVERSE_API_KEY",
}


def _config_dir() -> Path:
    return _Path(Path.home(), ".config", APP_NAME)


def _Path(*args: str | Path) -> Path:
    return Path(*args)


def load_env(path: str = ".env") -> None:
    env_file = _Path(path)
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


_config_cache: dict | None = None


def load_config() -> dict:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    config_path = _config_dir() / CONFIG_FILENAME
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                _config_cache = json.load(f)
                return _config_cache
        except json.JSONDecodeError:
            pass
    _config_cache = DEFAULT_CONFIG.copy()
    return _config_cache


def save_config(config: dict) -> None:
    global _config_cache
    config_dir = _config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / CONFIG_FILENAME
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    _config_cache = config


def reload_config() -> dict:
    global _config_cache
    _config_cache = None
    return load_config()


def get_api_key(provider: str) -> str | None:
    env_key = ENV_KEY_MAP.get(provider)
    if env_key:
        return os.environ.get(env_key)
    return None
