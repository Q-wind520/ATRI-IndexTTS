# ATRI-IndexTTS

统一 IndexTTS 模型 API 服务商接口 — 通过命令行统一调用各 IndexTTS 语音合成服务。

## 安装

```powershell
python -m uv sync
```

## 配置

### 1. API 密钥（`.env`）

在项目根目录创建 `.env` 文件：

```env
GITEE_AI_API_KEY=your_api_key
```

### 2. 全局配置（`~/.config/indextts/config.json`）

```powershell
indextts config set default_provider gitee
indextts config set gitee.base_url https://ai.gitee.com/v1
indextts config show
```

## 使用

```powershell
# TTS 合成（默认使用 Atri 声纹）
indextts tts "こんにちは"

# 指定声纹预设
indextts tts "こんにちは" -v Atri-2

# 自定义声纹参考
indextts tts "こんにちは" --prompt-audio "https://..." --prompt-text "参考文本"

# 查看可用语音
indextts voices

# 查看已配置服务商
indextts providers
```

> `indextts` 通过 `python -m uv run indextts` 运行。也可用 `python -m uv run main.py` 替代。

## 内置声纹预设

目前 `gitee` 服务商内置 3 组 ATRI 声纹预设：

| 语音角色 | 说明 |
|---------|------|
| `Atri` (默认) | `いえ、見えてましたよ。みなさんがいるの。わたし、目がいいので` |
| `Atri-2` | `わたしが夏生さんのために行動するのに、理由が必要でしょうか` |
| `Atri-3` | `間違いありません。知性の欠片も感じない、ジャカジャカとうるさいだけの音楽です` |

未指定 `--prompt-audio`/`--prompt-text` 时自动使用所选预设的声纹参考。

## 扩展服务商

1. 在 `src/atri_indextts/providers/` 下创建新文件，继承 `BaseTTSProvider`
2. 在 `src/atri_indextts/providers/__init__.py` 注册导出
3. 在 `src/atri_indextts/config.py` 添加 `ENV_KEY_MAP` 和 `DEFAULT_CONFIG`
4. 在 `src/atri_indextts/cli.py` 的 `_resolve_provider()` 添加分支

## 技术栈

- **CLI**: Click
- **API 客户端**: OpenAI (HTTP)
- **配置**: .env (敏感) + JSON (非敏感)
- **打包**: uv + pyproject.toml
