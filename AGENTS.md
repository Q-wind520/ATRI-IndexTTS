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
├── cli.py              # Click CLI entry point (tts, voices, providers, config)
├── config.py           # .env loader + ~/.config/indextts/config.json manager
├── models.py           # TTSRequest, TTSResponse, ProviderInfo dataclasses
├── providers/
│   ├── base.py         # Abstract base class (BaseTTSProvider)
│   └── gitee.py        # Gitee AI implementation (OpenAI-compatible API)
└── utils/audio.py      # Audio file save utility
```

- `main.py` — flat entry: delegates to `atri_indextts.cli:main`
- `test.py` — legacy proof-of-concept (Gitee AI IndexTTS-2 direct call)
- `tool.py` — empty placeholder

## CLI reference

```
indextts tts <text> [-p provider] [-v voice] [-o output] [--prompt-audio URL] [--prompt-text TEXT]
indextts voices [-p provider]
indextts providers
indextts config show
indextts config set <key> <value>          # key = default_provider 或 <provider>.base_url
```

## Config

- **Sensitive** → `.env` (gitignored): `GITEE_AI_API_KEY=your_key`
- **Non-sensitive** → `~/.config/indextts/config.json`:
  ```json
  { "default_provider": "gitee", "providers": { "gitee": { "base_url": "https://ai.gitee.com/v1" } } }
  ```

## Adding a new provider

1. Create `src/atri_indextts/providers/<name>.py` extending `BaseTTSProvider`
2. Register imports in `src/atri_indextts/providers/__init__.py`
3. Add `ENV_KEY_MAP` entry in `src/atri_indextts/config.py`
4. Add `_resolve_provider()` branch in `src/atri_indextts/cli.py`
5. Add provider defaults to `DEFAULT_CONFIG` in `src/atri_indextts/config.py`

## Gotchas

- **`uv` binary not on PATH** — always use `python -m uv`
- **`src/` layout** — package is `atri_indextts` (not `src`); imports use `from atri_indextts.xxx import ...`
- **Entry points** — after moving files or renaming modules, run `python -m uv sync` to rebuild the venv entry points
- **Windows encoding** — `sys.stdout.reconfigure(encoding="utf-8")` is set in cli.py for Chinese output
- **All dependencies must be declared in `pyproject.toml`** (currently: click, openai, requests)
- **`tool.uv.package = true`** in `pyproject.toml` enables entry point installation via `uv sync`
