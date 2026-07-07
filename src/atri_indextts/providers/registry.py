from typing import Type

from .base import BaseTTSProvider

_providers: dict[str, Type[BaseTTSProvider]] = {}


def register(name: str):
    def decorator(cls: Type[BaseTTSProvider]) -> Type[BaseTTSProvider]:
        _providers[name] = cls
        return cls

    return decorator


def get_provider_class(name: str) -> Type[BaseTTSProvider]:
    if name not in _providers:
        raise ValueError(f"未知服务商: {name}")
    return _providers[name]


def list_provider_names() -> list[str]:
    return list(_providers.keys())
