from hashlib import md5
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from ..voice_loader import AUDIO_DIR

AUDIO_TEMP_DIR = AUDIO_DIR / "temp"

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        _session.mount("https://", HTTPAdapter(max_retries=retries))
        _session.mount("http://", HTTPAdapter(max_retries=retries))
    return _session


def ensure_local_audio(source: str, cache_name: str | None = None) -> Path:
    if source.startswith(("http://", "https://")):
        if cache_name:
            local = AUDIO_TEMP_DIR / cache_name
        else:
            url_hash = md5(source.encode()).hexdigest()[:16]
            local = AUDIO_TEMP_DIR / f"url_{url_hash}.wav"

        if not local.exists():
            local.parent.mkdir(parents=True, exist_ok=True)
            resp = _get_session().get(source, timeout=180)
            resp.raise_for_status()
            local.write_bytes(resp.content)

        return local

    return Path(source)
