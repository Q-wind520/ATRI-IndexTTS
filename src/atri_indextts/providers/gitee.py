from openai import OpenAI

from ..models import ProviderInfo, TTSRequest, TTSResponse
from .base import BaseTTSProvider


class GiteeProvider(BaseTTSProvider):
    BASE_URL = "https://ai.gitee.com/v1"
    MODEL = "IndexTTS-2"
    DEFAULT_VOICES = ["Atri"]

    def __init__(self, api_key: str, base_url: str = BASE_URL):
        self._base_url = base_url
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        extra_body: dict = {}
        if request.prompt_audio:
            extra_body["prompt_audio_url"] = request.prompt_audio
        if request.prompt_text:
            extra_body["prompt_text"] = request.prompt_text

        response = self._client.audio.speech.create(
            model=self.MODEL,
            input=request.text,
            voice=request.voice,
            extra_body=extra_body,
        )

        return TTSResponse(audio=response.content, format="wav")

    def list_voices(self) -> list[str]:
        return self.DEFAULT_VOICES

    @property
    def name(self) -> str:
        return "gitee"

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            base_url=self._base_url,
            available_voices=self.DEFAULT_VOICES,
        )
