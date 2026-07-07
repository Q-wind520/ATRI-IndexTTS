from openai import OpenAI

from ..models import ProviderInfo, TTSRequest, TTSResponse
from ..voice_loader import get_voice, list_voice_names
from .base import BaseTTSProvider
from .registry import register


@register("gitee")
class GiteeProvider(BaseTTSProvider):
    BASE_URL = "https://ai.gitee.com/v1"
    MODEL = "IndexTTS-2"

    def __init__(self, api_key: str | None = None, base_url: str = BASE_URL):
        self._api_key = api_key
        self._base_url = base_url
        self._client: OpenAI | None = None

    def _ensure_client(self):
        if self._client is not None:
            return
        if not self._api_key:
            raise ValueError("未设置 GITEE_AI_API_KEY，请在 .env 中配置")
        self._client = OpenAI(base_url=self._base_url, api_key=self._api_key, timeout=600.0, max_retries=2)

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        self._ensure_client()
        assert self._client is not None

        voice = request.voice
        voice_obj = get_voice(voice) if voice else None

        prompt_audio = request.prompt_audio
        prompt_text = request.prompt_text

        if voice_obj and voice_obj.prompts:
            idx = min(max(request.prompt_index, 0), len(voice_obj.prompts) - 1)
            preset = voice_obj.prompts[idx]
            if not prompt_audio:
                prompt_audio = preset.prompt_audio_url
            if not prompt_text:
                prompt_text = preset.prompt_text

        if not prompt_audio:
            raise ValueError(
                "请选择声纹预设 (-v Atri) 或提供 --prompt-audio"
            )

        extra_body: dict = {}
        if prompt_audio:
            extra_body["prompt_audio_url"] = prompt_audio
        if prompt_text:
            extra_body["prompt_text"] = prompt_text
        if request.emo_audio:
            extra_body["emo_audio"] = request.emo_audio
        if request.emo_alpha is not None:
            extra_body["emo_alpha"] = request.emo_alpha
        if request.emo_text:
            extra_body["emo_text"] = request.emo_text

        response = self._client.audio.speech.create(
            model=self.MODEL,
            input=request.text,
            voice="Atri",
            extra_body=extra_body,
        )

        return TTSResponse(audio=response.content, format="wav")

    def list_voices(self) -> list[str]:
        return list_voice_names()

    @property
    def name(self) -> str:
        return "gitee"

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            base_url=self._base_url,
            available_voices=list_voice_names(),
        )
