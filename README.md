# ATRI-IndexTTS

统一 IndexTTS 模型 API 服务商接口 — 通过命令行统一调用各 IndexTTS 语音合成服务。

## 安装

```powershell
# 克隆项目
git clone <repo-url>
cd ATRI-IndexTTS

# 安装依赖与入口
python -m uv sync
```

## 配置

### 1. API 密钥（`.env`）

在项目根目录创建 `.env` 文件：

```env
GITEE_AI_API_KEY=your_api_key
```

### 2. 全局配置（`~/.config/indextts/config.json`）

首次运行自动生成默认配置，也可手动编辑：

```json
{
  "default_provider": "gitee",
  "providers": {
    "gitee": {
      "base_url": "https://ai.gitee.com/v1"
    }
  }
}
```

通过 CLI 修改：

```powershell
indextts config set default_provider gitee
indextts config set gitee.base_url https://ai.gitee.com/v1
indextts config show
```

## 使用

```powershell
# TTS 合成
indextts tts "你好，世界"

# 指定语音、输出路径、声纹参考
indextts tts "你好" -v Atri -o output.wav --prompt-audio "https://..." --prompt-text "参考文本"

# 查看可用语音
indextts voices -p gitee

# 查看已配置服务商
indextts providers
```

> `indextts` 通过 `python -m uv run indextts` 运行。也可用 `python -m uv run main.py` 替代。

## 扩展服务商

1. 在 `src/atri_indextts/providers/` 下创建新文件，继承 `BaseTTSProvider`
2. 在 `src/atri_indextts/providers/__init__.py` 注册导出
3. 在 `src/atri_indextts/config.py` 添加 `ENV_KEY_MAP` 和 `DEFAULT_CONFIG`
4. 在 `src/atri_indextts/cli.py` 的 `_resolve_provider()` 添加分支
