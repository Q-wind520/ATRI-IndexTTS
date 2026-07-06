# ATRI-IndexTTS

统一 IndexTTS 模型 API 服务商接口 — 通过命令行统一调用各 IndexTTS 语音合成服务。

支持 **Gitee AI** 和 **AstraFlow (ModelVerse)** 双服务商。

## 安装

```powershell
python -m uv sync
```

## 配置

### 1. API 密钥（`.env`）

在项目根目录创建 `.env` 文件：

```env
GITEE_AI_API_KEY=your_gitee_key
MODELVERSE_API_KEY=your_astraflow_key
```

### 2. 全局配置（`~/.config/indextts/config.json`）

```powershell
indextts config set default_provider astraflow
indextts config set gitee.base_url https://ai.gitee.com/v1
indextts config set astraflow.base_url https://api.modelverse.cn/v1
indextts config show
```

## 使用

```powershell
# 指定服务商和声纹预设进行合成
indextts tts "你好" -p gitee -v Atri

# 选择参考声纹（每段声纹对应不同语气）
indextts tts "你好" -p astraflow -v Atri --prompt-index 1

# 自定义声纹参考（覆盖预设）
indextts tts "你好" --prompt-audio "https://..." --prompt-text "参考文本"

# 情感控制
indextts tts "你好" -p astraflow -v Atri --emo-text "很激动" --emo-alpha 0.8
indextts tts "你好" -p astraflow -v Atri --emo-audio "https://..." --emo-alpha 0.5

# 查看可用声纹
indextts voices

# 查看已配置服务商
indextts providers

# 设为默认服务商（后续可省略 -p）
indextts config set default_provider astraflow
indextts tts "你好" -v Atri
```

> `indextts` 通过 `python -m uv run indextts` 运行。也可用 `python -m uv run main.py` 替代。

## 内置声纹

声纹数据存储在 `src/atri_indextts/voices.json`，不归属任何服务商，支持多段参考音频切换：

```
可用音色:
  Atri (3 参考声纹)
    [0] 日常说话
    [1] 疑问语气
    [2] 冷淡语气
```

选择 `-v Atri` 后默认使用 `[0]`，通过 `--prompt-index` 切换。

## 服务商对比

| 特性 | Gitee AI | AstraFlow (ModelVerse) |
|------|----------|------------------------|
| 协议 | OpenAI JSON | multipart/form-data |
| 参考音频 | URL 直传 | 文件上传（自动缓存到 `audio/temp/`） |
| 声纹预设 | ✅ 共享 `voices.json` | ✅ 共享 `voices.json` |
| 情感控制 | ✅ `emo_audio`/`emo_text` | ✅ `emo_audio`/`emo_text` + 自动推断 `emo_control_method` |
| 合成效果 | IndexTTS-2 | IndexTTS-2 |

Gitee 的参考音频通过 URL 直传；AstraFlow 需上传二进制文件，首次使用时会自动下载并缓存到 `src/atri_indextts/audio/temp/`，后续复用跳过下载。

## 扩展服务商

1. 在 `src/atri_indextts/providers/` 下创建新文件，继承 `BaseTTSProvider`
2. 在 `src/atri_indextts/providers/__init__.py` 注册导出
3. 在 `src/atri_indextts/config.py` 添加 `ENV_KEY_MAP` 和 `DEFAULT_CONFIG`
4. 在 `src/atri_indextts/service.py` 的 `_resolve_provider()` 添加分支
