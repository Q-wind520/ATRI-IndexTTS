# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] — 2026-07-07

### Added
- **Provider 注册表模式**: `providers/registry.py` 装饰器注册，替代硬编码 if/elif 分发 (`#5`)
- **流式合成 `indextts tts --stream`**: 按句号/感叹号/问号逐句合成 (`#11`)
- **声纹管理 `indextts voice add`**: CLI 管理声纹预设，无需手动编辑 JSON (`#12`)
- **可配置默认输出目录 `indextts config set output_dir`**: 支持自定义输出路径 (`#13`)

### Changed
- **voice_loader**: 添加内存缓存，避免重复解析 JSON (`#8`)

### Fixed
- **AGENTS.md**: 更新架构图、CLI 参考和新增 Provider 步骤 (`#10`)

---

## [1.1.0] — 2026-07-06

### Added
- **音频缓存 `utils/audio_cache.py`**: 提取 AstraFlow 的内部下载逻辑为独立模块 (`#6`)
- **配置内存缓存**: `config.py` 添加 `_config_cache` + `reload_config()` (`#7`)
- **单元测试**: 46 个测试覆盖 config、providers、service、voice_loader (`#1`)

### Changed
- **Provider 构造**: 适配 `ensure_local_audio` 调用

### Fixed
- **HTTP 超时**: `requests.post()` 添加 `timeout=600`；`OpenAI` client 添加 `timeout=600.0, max_retries=2` (`#2`)
- **重复 POST 逻辑**: astraflow.py 的 `requests.post()` 去重，合并为一次调用 (`#3`)
- **HTTP 重试**: 所有 HTTP 请求使用 `urllib3.Retry` + `HTTPAdapter` (`#4`)
- **egg-info 过期**: `uv sync` 更新 SOURCES.txt (`#9`)

---

## [1.0.1] — 2026-07-04

### Added
- **AstraFlow (ModelVerse) 服务商**: 支持 IndexTTS-2 模型的 multipart upload API
- **情感控制**: `--emo-audio`, `--emo-alpha`, `--emo-text` 参数
- **声纹缓存**: 下载的参考音频缓存到 `audio/temp/`

### Changed
- 重构 TTS 服务架构，添加 TTSService 编排层
- 优化 CLI 接口，统一服务商调用

---

## [1.0.0] — 2026-07-02

### Added
- 初始版本
- **Gitee AI 服务商**: 支持 IndexTTS-2 模型 (OpenAI 兼容 API)
- **声纹预设 `voices.json`**: Atri 角色，3 种语气
- **CLI 命令**: `tts`, `voices`, `providers`, `config show/set`
- `.env` 配置管理 + `~/.config/indextts/config.json`
