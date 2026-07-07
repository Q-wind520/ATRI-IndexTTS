from dataclasses import dataclass, field


@dataclass
class TTSRequest:
    text: str
    voice: str | None = None
    prompt_audio: str | None = None
    prompt_text: str | None = None
    emo_audio: str | None = None
    emo_alpha: float | None = None
    emo_text: str | None = None
    prompt_index: int = 0
    provider: str = "gitee"
    format: str = "wav"


@dataclass
class TTSResponse:
    audio: bytes
    format: str = "wav"


@dataclass
class ProviderInfo:
    name: str
    base_url: str
    available_voices: list[str] = field(default_factory=list)
