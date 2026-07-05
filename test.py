import os
import sys
from pathlib import Path
from openai import OpenAI

def load_env(path=".env"):
    env_file = Path(path)
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

load_env()

API_KEY = os.environ.get("GITEE_AI_API_KEY")
if not API_KEY:
    raise ValueError("请将 API Key 写入 .env 文件: GITEE_AI_API_KEY=your_key")

BASE = "https://ai.gitee.com"

audio_dir = Path("voice")
audio_files = list(audio_dir.glob("*.wav"))
if not audio_files:
    raise FileNotFoundError("voice/ 目录下没有找到 .wav 文件")

prompt_path = audio_files[0]
prompt_text = prompt_path.stem

if len(sys.argv) > 1:
    file_url = sys.argv[1]
else:
    file_url = os.environ.get("PROMPT_AUDIO_URL")
    if not file_url:
        raise ValueError(
            "请将音频上传到公开仓库后，通过环境变量 PROMPT_AUDIO_URL 或命令行参数传入 raw URL\n"
            f"例: python test.py https://gitee.com/xxx/xxx/raw/master/{prompt_path.name}"
        )

client = OpenAI(base_url=f"{BASE}/v1", api_key=API_KEY)
response = client.audio.speech.create(
    model="IndexTTS-2",
    input="你好，我是一个由IndexTTS-2生成的语音测试。",
    voice="Atri",
    extra_body={
        "prompt_audio_url": file_url,
        "prompt_text": prompt_text,
    },
)

output_path = os.path.join("temp", "output", "indextts2_test.wav")
with open(output_path, "wb") as f:
    f.write(response.content)

print(f"语音文件已生成: {output_path}")
print(f"声纹文本: {prompt_text}")
