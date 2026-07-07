import json
from hashlib import md5
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from ..models import ProviderInfo, TTSRequest, TTSResponse
from ..utils.audio_cache import ensure_local_audio
from ..voice_loader import get_voice, list_voice_names
from .base import BaseTTSProvider


class AstraFlowProvider(BaseTTSProvider):
    BASE_URL = "https://api.modelverse.cn/v1"
    MODEL = "IndexTeam/IndexTTS-2"

    def __init__(self, api_key: str | None = None, base_url: str = BASE_URL):
        self._api_key = api_key
        self._base_url = base_url
        self._session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        self._session.mount("https://", HTTPAdapter(max_retries=retries))
        self._session.mount("http://", HTTPAdapter(max_retries=retries))

    @property
    def _auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}"}

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
                spk_audio_path = ensure_local_audio(
                    prompt.prompt_audio_url, cache_name
                )
        elif request.prompt_audio:
            cache_name = f"prompt_{md5(request.prompt_audio.encode()).hexdigest()[:16]}.wav"
            spk_audio_path = ensure_local_audio(
                request.prompt_audio, cache_name
            )

        if not spk_audio_path:
            raise ValueError(
                "请选择声纹预设 (-v Atri) 或提供 --prompt-audio"
            )

        if request.emo_audio:
            cache_name = f"emo_{md5(request.emo_audio.encode()).hexdigest()[:16]}.wav"
            emo_audio_path = ensure_local_audio(
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

        emo_file = None
        with open(spk_audio_path, "rb") as f:
            files_payload["spk_audio_file"] = (
                spk_audio_path.name,
                f,
                "audio/wav",
            )
            try:
                if emo_audio_path:
                    emo_file = open(emo_audio_path, "rb")
                    files_payload["emo_audio_file"] = (
                        emo_audio_path.name,
                        emo_file,
                        "audio/wav",
                    )
                resp = self._session.post(
                    f"{self._base_url}/audio/infer",
                    headers=self._auth_header,
                    files=files_payload,
                    timeout=600,
                )
            finally:
                if emo_file:
                    emo_file.close()

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
