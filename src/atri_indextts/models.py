from dataclasses import dataclass, field


@dataclass
class TTSRequest:
    text: str
    voice: str = "Atri"
    prompt_audio: str | None = None
    prompt_text: str | None = None
    provider: str = "gitee"


@dataclass
class TTSResponse:
    audio: bytes
    format: str = "wav"


@dataclass
class ProviderInfo:
    name: str
    base_url: str
    available_voices: list[str] = field(default_factory=list)
