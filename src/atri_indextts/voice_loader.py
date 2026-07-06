import json
from pathlib import Path

_VOICES_PATH = Path(__file__).parent / "voices.json"


class VoicePrompt:
    def __init__(self, label: str, description: str | None, prompt_audio_url: str, prompt_text: str):
        self.label = label
        self.description = description
        self.prompt_audio_url = prompt_audio_url
        self.prompt_text = prompt_text


class Voice:
    def __init__(self, name: str, prompts: list[VoicePrompt]):
        self.name = name
        self.prompts = prompts

    @property
    def prompt_count(self) -> int:
        return len(self.prompts)


def _load_data() -> list[dict]:
    with open(_VOICES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("voices", [])


def load_voices() -> list[Voice]:
    result: list[Voice] = []
    for v in _load_data():
        prompts = [
            VoicePrompt(
                label=p["label"],
                description=p.get("description"),
                prompt_audio_url=p["prompt_audio_url"],
                prompt_text=p["prompt_text"],
            )
            for p in v.get("prompts", [])
        ]
        result.append(Voice(name=v["name"], prompts=prompts))
    return result


def get_voice(name: str) -> Voice | None:
    for v in load_voices():
        if v.name == name:
            return v
    return None


def list_voice_names() -> list[str]:
    return [v["name"] for v in _load_data()]
