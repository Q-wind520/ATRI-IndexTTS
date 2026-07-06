import json
from hashlib import md5
from pathlib import Path

import requests

from ..models import ProviderInfo, TTSRequest, TTSResponse
from ..voice_loader import AUDIO_DIR, get_voice, list_voice_names
from .base import BaseTTSProvider

_AUDIO_TEMP_DIR = AUDIO_DIR / "temp"


class AstraFlowProvider(BaseTTSProvider):
    BASE_URL = "https://api.modelverse.cn/v1"
    MODEL = "IndexTeam/IndexTTS-2"

    def __init__(self, api_key: str | None = None, base_url: str = BASE_URL):
        self._api_key = api_key
        self._base_url = base_url

    @property
    def _auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}"}

    @staticmethod
    def _ensure_local_audio(source: str, cache_name: str | None = None) -> Path:
        if source.startswith(("http://", "https://")):
            if cache_name:
                local = _AUDIO_TEMP_DIR / cache_name
            else:
                url_hash = md5(source.encode()).hexdigest()[:16]
                local = _AUDIO_TEMP_DIR / f"url_{url_hash}.wav"

            if not local.exists():
                local.parent.mkdir(parents=True, exist_ok=True)
                resp = requests.get(source)
                resp.raise_for_status()
                local.write_bytes(resp.content)

            return local

        return Path(source)

    @staticmethod
    def _infer_emo_control_method(request: TTSRequest) -> int:
        if request.emo_audio:
            return 1
        if request.emo_text:
            return 3
        return 0

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        if not self._api_key:
            raise ValueError("未设置 MODELVERSE_API_KEY，请在 .env 中配置")

        spk_audio_source: str | None = None
        spk_audio_path: Path | None = None
        emo_audio_path: Path | None = None

        voice_obj = get_voice(request.voice) if request.voice else None

        if voice_obj and voice_obj.prompts:
            idx = min(max(request.prompt_index, 0), len(voice_obj.prompts) - 1)
            prompt = voice_obj.prompts[idx]
            if prompt.local_path:
                spk_audio_path = prompt.local_path
            else:
                cache_name = f"{request.voice}_{idx}.wav"
                spk_audio_path = self._ensure_local_audio(
                    prompt.prompt_audio_url, cache_name
                )
        elif request.prompt_audio:
            cache_name = f"prompt_{md5(request.prompt_audio.encode()).hexdigest()[:16]}.wav"
            spk_audio_path = self._ensure_local_audio(
                request.prompt_audio, cache_name
            )

        if not spk_audio_path:
            raise ValueError(
                "请选择声纹预设 (-v Atri) 或提供 --prompt-audio"
            )

        if request.emo_audio:
            cache_name = f"emo_{md5(request.emo_audio.encode()).hexdigest()[:16]}.wav"
            emo_audio_path = self._ensure_local_audio(
                request.emo_audio, cache_name
            )

        payload = {
            "input": request.text,
            "sample_rate": 22050,
            "speed": 1.0,
            "emo_control_method": self._infer_emo_control_method(request),
        }

        if request.emo_alpha is not None:
            payload["emo_alpha"] = request.emo_alpha
        if request.emo_text:
            payload["emo_text"] = request.emo_text

        files_payload: dict = {
            "model": (None, self.MODEL),
            "payload": (None, json.dumps(payload)),
        }

        with open(spk_audio_path, "rb") as f:
            files_payload["spk_audio_file"] = (
                spk_audio_path.name,
                f,
                "audio/wav",
            )
            if emo_audio_path:
                with open(emo_audio_path, "rb") as ef:
                    files_payload["emo_audio_file"] = (
                        emo_audio_path.name,
                        ef,
                        "audio/wav",
                    )
                    resp = requests.post(
                        f"{self._base_url}/audio/infer",
                        headers=self._auth_header,
                        files=files_payload,
                    )
            else:
                resp = requests.post(
                    f"{self._base_url}/audio/infer",
                    headers=self._auth_header,
                    files=files_payload,
                )

        if not resp.ok:
            try:
                err = resp.json()
                msg = err.get("error", {}).get("message", resp.text)
            except json.JSONDecodeError:
                msg = resp.text
            raise ValueError(f"AstraFlow API 错误 ({resp.status_code}): {msg}")

        return TTSResponse(audio=resp.content, format="wav")

    def list_voices(self) -> list[str]:
        return list_voice_names()

    @property
    def name(self) -> str:
        return "astraflow"

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            base_url=self._base_url,
            available_voices=list_voice_names(),
        )
