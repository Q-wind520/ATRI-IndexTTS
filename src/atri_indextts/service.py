from pathlib import Path
import re

from .config import get_api_key, load_config, load_env, reload_config, save_config
from .models import TTSRequest
from .providers import get_provider_class
from .voice_loader import load_voices


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？.!?；;])\s*")


class TTSService:
    def __init__(self):
        load_env()

    @property
    def _config(self):
        return load_config()

    def _resolve_provider(self, name: str):
        cls = get_provider_class(name)
        api_key = get_api_key(name)
        base_url = self._config.get("providers", {}).get(name, {}).get(
            "base_url", cls.BASE_URL
        )
        return cls(api_key=api_key, base_url=base_url)

    def _get_provider_name(self, provider: str | None = None) -> str:
        if provider:
            return provider
        name = self._config.get("default_provider")
        if not name:
            raise ValueError(
                "请指定服务商：-p gitee，或设置默认服务商：indextts config set default_provider gitee"
            )
        return name

    def _get_output_path(self, output: str | None = None) -> str:
        if output is not None:
            return output
        return str(
            Path(self._config.get("output_dir", "temp/output"))
            / "indextts.wav"
        )

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        parts = _SENTENCE_SPLIT_RE.split(text)
        return [p.strip() for p in parts if p.strip()]

    def _build_request(
        self,
        text: str,
        provider_name: str,
        voice: str | None = None,
        prompt_audio: str | None = None,
        prompt_text: str | None = None,
        emo_audio: str | None = None,
        emo_alpha: float | None = None,
        emo_text: str | None = None,
        prompt_index: int = 0,
    ) -> TTSRequest:
        return TTSRequest(
            text=text,
            voice=voice,
            prompt_audio=prompt_audio,
            prompt_text=prompt_text,
            emo_audio=emo_audio,
            emo_alpha=emo_alpha,
            emo_text=emo_text,
            prompt_index=prompt_index,
            provider=provider_name,
        )

    def synthesize(
        self,
        text: str,
        provider: str | None = None,
        voice: str | None = None,
        output: str | None = None,
        prompt_audio: str | None = None,
        prompt_text: str | None = None,
        emo_audio: str | None = None,
        emo_alpha: float | None = None,
        emo_text: str | None = None,
        prompt_index: int = 0,
    ) -> Path:
        provider_name = self._get_provider_name(provider)
        prov = self._resolve_provider(provider_name)

        output = self._get_output_path(output)

        request = self._build_request(
            text=text,
            provider_name=provider_name,
            voice=voice,
            prompt_audio=prompt_audio,
            prompt_text=prompt_text,
            emo_audio=emo_audio,
            emo_alpha=emo_alpha,
            emo_text=emo_text,
            prompt_index=prompt_index,
        )

        response = prov.synthesize(request)

        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(response.audio)

        return out_path

    def synthesize_stream(
        self,
        text: str,
        provider: str | None = None,
        voice: str | None = None,
        output_dir: str | None = None,
        prompt_audio: str | None = None,
        prompt_text: str | None = None,
        emo_audio: str | None = None,
        emo_alpha: float | None = None,
        emo_text: str | None = None,
        prompt_index: int = 0,
    ) -> list[Path]:
        provider_name = self._get_provider_name(provider)
        prov = self._resolve_provider(provider_name)

        if output_dir is None:
            output_dir = self._config.get("output_dir", "temp/output")
        out_dir = Path(output_dir)

        sentences = self._split_sentences(text)
        if not sentences:
            sentences = [text]

        result: list[Path] = []
        total = len(sentences)
        for i, sentence in enumerate(sentences):
            request = self._build_request(
                text=sentence,
                provider_name=provider_name,
                voice=voice,
                prompt_audio=prompt_audio,
                prompt_text=prompt_text,
                emo_audio=emo_audio,
                emo_alpha=emo_alpha,
                emo_text=emo_text,
                prompt_index=prompt_index,
            )

            response = prov.synthesize(request)

            out_path = out_dir / f"chunk_{i:03d}.wav"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(response.audio)
            result.append(out_path)

        return result

    def list_voices(self):
        from .voice_loader import Voice
        return load_voices()

    def list_providers(self) -> dict:
        config = self._config
        default = config.get("default_provider")
        result: dict = {"default": default, "providers": {}}
        for name, details in config.get("providers", {}).items():
            result["providers"][name] = {
                "base_url": details.get("base_url", "N/A"),
            }
        return result

    def get_config(self) -> dict:
        config_data = load_config()
        api_keys = {}
        for provider_name in config_data.get("providers", {}):
            key = get_api_key(provider_name)
            api_keys[provider_name] = "***" if key else None
        return {
            "default_provider": config_data.get("default_provider"),
            "providers": config_data.get("providers", {}),
            "api_keys": api_keys,
        }

    def set_config(self, key: str, value: str) -> None:
        config_data = load_config()
        if key == "default_provider":
            config_data["default_provider"] = value
        elif key == "output_dir":
            config_data["output_dir"] = value
        elif "." in key:
            provider_name, field = key.split(".", 1)
            if provider_name not in config_data.get("providers", {}):
                config_data.setdefault("providers", {})[provider_name] = {}
            config_data["providers"][provider_name][field] = value
        else:
            raise ValueError(
                f"未知配置项: {key}，支持: default_provider, output_dir, <provider>.base_url"
            )
        save_config(config_data)
        reload_config()
