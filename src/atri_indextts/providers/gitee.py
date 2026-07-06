from openai import OpenAI

from ..models import ProviderInfo, TTSRequest, TTSResponse
from .base import BaseTTSProvider

_BASE = "https://gitee.com/q_wind520/TTSVoiceRope/raw/master/voice/ATRI-亚托莉"

PROMPT_PRESETS: dict[str, dict[str, str]] = {
    "Atri": {
        "prompt_audio_url": f"{_BASE}/いえ、見えてましたよ。みなさんがいるの。わたし、目がいいので.wav",
        "prompt_text": "いえ、見えてましたよ。みなさんがいるの。わたし、目がいいので",
    },
    "Atri-2": {
        "prompt_audio_url": f"{_BASE}/わたしが夏生さんのために行動するのに、理由が必要でしょうか.wav",
        "prompt_text": "わたしが夏生さんのために行動するのに、理由が必要でしょうか",
    },
    "Atri-3": {
        "prompt_audio_url": f"{_BASE}/間違いありません。知性の欠片も感じない、ジャカジャカとうるさいだけの音楽です.wav",
        "prompt_text": "間違いありません。知性の欠片も感じない、ジャカジャカとうるさいだけの音楽です",
    },
}


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
        self._client = OpenAI(base_url=self._base_url, api_key=self._api_key)

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        self._ensure_client()

        voice = request.voice
        preset = PROMPT_PRESETS.get(voice)

        prompt_audio = request.prompt_audio
        prompt_text = request.prompt_text

        if preset:
            if not prompt_audio:
                prompt_audio = preset["prompt_audio_url"]
            if not prompt_text:
                prompt_text = preset["prompt_text"]

        if not prompt_audio:
            raise ValueError(
                "请选择声纹预设 (-v Atri / Atri-2 / Atri-3) 或提供 --prompt-audio"
            )

        extra_body: dict = {}
        if prompt_audio:
            extra_body["prompt_audio_url"] = prompt_audio
        if prompt_text:
            extra_body["prompt_text"] = prompt_text

        response = self._client.audio.speech.create(
            model=self.MODEL,
            input=request.text,
            voice="Atri",
            extra_body=extra_body,
        )

        return TTSResponse(audio=response.content, format="wav")

    def list_voices(self) -> list[str]:
        return list(PROMPT_PRESETS.keys())

    @property
    def name(self) -> str:
        return "gitee"

    @property
    def info(self) -> ProviderInfo:
        return ProviderInfo(
            name=self.name,
            base_url=self._base_url,
            available_voices=list(PROMPT_PRESETS.keys()),
        )
