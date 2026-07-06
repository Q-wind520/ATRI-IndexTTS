from pathlib import Path


def save_audio(audio: bytes, output: str | Path, mkdir: bool = True) -> Path:
    path = Path(output)
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(audio)
    return path
