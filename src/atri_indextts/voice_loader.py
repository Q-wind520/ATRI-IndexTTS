import json
from pathlib import Path

_VOICES_PATH = Path(__file__).parent / "voices.json"
AUDIO_DIR = Path(__file__).parent / "audio"
_cached_data: list[dict] | None = None


class VoicePrompt:
    def __init__(self, label: str, description: str | None, prompt_audio_url: str, prompt_text: str):
        self.label = label
        self.description = description
        self.prompt_audio_url = prompt_audio_url
        self.prompt_text = prompt_text
        self.local_path: Path | None = None


class Voice:
    def __init__(self, name: str, prompts: list[VoicePrompt], description: str | None = None):
        self.name = name
        self.prompts = prompts
        self.description = description

    @property
    def prompt_count(self) -> int:
        return len(self.prompts)


def _resolve_prompt_audio(name: str, index: int) -> Path | None:
    for ext in (".wav", ".mp3"):
        p = AUDIO_DIR / f"{name}_{index}{ext}"
        if p.exists():
            return p
        p = AUDIO_DIR / "temp" / f"{name}_{index}{ext}"
        if p.exists():
            return p
    return None


def _load_data() -> list[dict]:
    global _cached_data
    if _cached_data is not None:
        return _cached_data
    with open(_VOICES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    _cached_data = data.get("voices", [])
    return _cached_data


def clear_voice_cache() -> None:
    global _cached_data
    _cached_data = None


def _build_prompts(name: str, prompts_data: list[dict]) -> list[VoicePrompt]:
    prompts: list[VoicePrompt] = []
    for i, p in enumerate(prompts_data):
        prompt = VoicePrompt(
            label=p["label"],
            description=p.get("description"),
            prompt_audio_url=p["prompt_audio_url"],
            prompt_text=p["prompt_text"],
        )
        prompt.local_path = _resolve_prompt_audio(name, i)
        prompts.append(prompt)
    return prompts


def load_voices() -> list[Voice]:
    result: list[Voice] = []
    for v in _load_data():
        prompts = _build_prompts(v["name"], v.get("prompts", []))
        result.append(Voice(name=v["name"], prompts=prompts, description=v.get("description")))
    return result


def get_voice(name: str) -> Voice | None:
    for v in _load_data():
        if v["name"] == name:
            prompts = _build_prompts(v["name"], v.get("prompts", []))
            return Voice(name=v["name"], prompts=prompts, description=v.get("description"))
    return None


def list_voice_names() -> list[str]:
    return [v["name"] for v in _load_data()]


def add_voice_to_file(
    name: str,
    label: str,
    prompt_audio_url: str,
    prompt_text: str,
    description: str | None = None,
) -> bool:
    with open(_VOICES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    voices: list[dict] = data.get("voices", [])

    new_prompt: dict = {
        "label": label,
        "prompt_audio_url": prompt_audio_url,
        "prompt_text": prompt_text,
    }
    if description is not None:
        new_prompt["description"] = description

    for voice in voices:
        if voice.get("name") == name:
            voice.setdefault("prompts", []).append(new_prompt)
            break
    else:
        voices.append({
            "name": name,
            "prompts": [new_prompt],
        })

    data["voices"] = voices
    with open(_VOICES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    clear_voice_cache()
    return True
