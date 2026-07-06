# AGENTS.md — ATRI-IndexTTS

## Commands

- **Run**: `python -m uv run main.py`
- **Add deps**: `python -m uv add <package>` (updates `pyproject.toml` + lock)
- **Activate venv**: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` → `.venv\Scripts\Activate.ps1`
- **Run project scripts**: `python -m uv run <script.py>` (uv auto-resolves venv)

## Architecture

- `main.py` — entry point (stub, prints hello)
- `test.py` — Gitee AI IndexTTS-2 API caller
- `tool.py` — empty, placeholder

## test.py requirements

- Requires `.env` file with `GITEE_AI_API_KEY=your_key` (not tracked via `.gitignore`)
- Requires `voice/*.wav` files for prompt audio; filename stem used as prompt text
- Requires `openai` package (`python -m uv add openai`)
- Usage: `python -m uv run test.py [prompt_audio_raw_url]`
- If no URL arg, reads `PROMPT_AUDIO_URL` env var
- Output: `temp/output/indextts2_test.wav`

## Gotchas

- `uv` binary not on PATH — always use `python -m uv`
- All dependencies must be declared in `pyproject.toml` (currently only `requests`)
