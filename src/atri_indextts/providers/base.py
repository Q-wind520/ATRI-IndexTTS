from abc import ABC, abstractmethod

from ..models import ProviderInfo, TTSRequest, TTSResponse


class BaseTTSProvider(ABC):
    @abstractmethod
    def synthesize(self, request: TTSRequest) -> TTSResponse: ...

    @abstractmethod
    def list_voices(self) -> list[str]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def info(self) -> ProviderInfo: ...

    @property
    def supported_formats(self) -> list[str]:
        return ["wav"]
