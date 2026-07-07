# AGENTS.md — ATRI-IndexTTS

## Commands

- **Run**: `python -m uv run indextts <command>` or `python -m uv run main.py <command>`
- **Direct subcommand**: `python -m uv run indextts tts "hello"`
- **Add deps**: `python -m uv add <package>` (updates `pyproject.toml` + lock)
- **Sync venv**: `python -m uv sync` (reinstalls entry points after structural changes)
- **Activate venv**: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` → `.venv\Scripts\Activate.ps1`

## Architecture

```
src/atri_indextts/
├── cli.py              # Click CLI entry point (tts, voices, providers, config, voice add)
├── config.py           # .env loader + ~/.config/indextts/config.json manager (with memory cache)
├── models.py           # TTSRequest, TTSResponse, ProviderInfo dataclasses
├── service.py          # TTSService: orchestration layer (resolve → synthesize)
├── voice_loader.py     # Voice preset loader from voices.json (with memory cache)
├── voices.json         # Voice preset definitions (Atri with 3 tones)
├── providers/
│   ├── base.py         # Abstract base class (BaseTTSProvider)
│   ├── registry.py     # Decorator-based provider registry (@register + get_provider_class)
│   ├── gitee.py        # Gitee AI implementation (OpenAI-compatible API)
│   └── astraflow.py    # AstraFlow (ModelVerse) implementation (multipart upload)
└── utils/
    ├── audio.py         # Audio file save utility
    └── audio_cache.py   # Shared audio download/cache with retry
```

- `main.py` — flat entry: delegates to `atri_indextts.cli:main`
- `test.py` — legacy proof-of-concept (Gitee AI IndexTTS-2 direct call)

## CLI reference

```
indextts tts <text> [-p provider] [-v voice] [-o output] [--prompt-audio URL] [--prompt-text TEXT] [--emo-audio URL] [--emo-alpha 0.5] [--emo-text TEXT] [--prompt-index N] [--stream]
indextts voices [-p provider]
indextts providers
indextts config show
indextts config set <key> <value>          # key = default_provider, output_dir, <provider>.base_url
indextts voice add <name> --label STRING --prompt-audio URL --prompt-text TEXT [--description TEXT]
```

## Config

- **Sensitive** → `.env` (gitignored): `GITEE_AI_API_KEY=your_key`
- **Non-sensitive** → `~/.config/indextts/config.json`:
  ```json
  { "default_provider": "gitee", "providers": { "gitee": { "base_url": "https://ai.gitee.com/v1" } } }
  ```

## Adding a new provider

1. Create `src/atri_indextts/providers/<name>.py` extending `BaseTTSProvider` with `@register("<name>")` decorator
2. Import the module in `src/atri_indextts/providers/__init__.py` (triggers registration)
3. Add `ENV_KEY_MAP` entry in `src/atri_indextts/config.py`
4. Add provider defaults to `DEFAULT_CONFIG` in `src/atri_indextts/config.py`

## Gotchas

- **`uv` binary not on PATH** — always use `python -m uv`
- **`src/` layout** — package is `atri_indextts` (not `src`); imports use `from atri_indextts.xxx import ...`
- **Entry points** — after moving files or renaming modules, run `python -m uv sync` to rebuild the venv entry points
- **Windows encoding** — `sys.stdout.reconfigure(encoding="utf-8")` is set in cli.py for Chinese output
- **All dependencies must be declared in `pyproject.toml`** (currently: click, openai, requests)
- **`tool.uv.package = true`** in `pyproject.toml` enables entry point installation via `uv sync`
