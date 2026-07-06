import os
import argparse
from pathlib import Path
from openai import OpenAI

DEFAULT_PROMPT_URL = "https://gitee.com/q_wind520/TTSVoiceRope/raw/master/voice/ATRI-%E4%BA%9A%E6%89%98%E8%8E%89/%E3%81%84%E3%81%88%E3%80%81%E8%A6%8B%E3%81%88%E3%81%A6%E3%81%BE%E3%81%97%E3%81%9F%E3%82%88%E3%80%82%E3%81%BF%E3%81%AA%E3%81%95%E3%82%93%E3%81%8C%E3%81%84%E3%82%8B%E3%81%AE%E3%80%82%E3%82%8F%E3%81%9F%E3%81%97%E3%80%81%E7%9B%AE%E3%81%8C%E3%81%84%E3%81%84%E3%81%AE%E3%81%A7.wav"

def load_env(path=".env"):
    env_file = Path(path)
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

load_env()

parser = argparse.ArgumentParser(description="IndexTTS-2 语音合成测试")
parser.add_argument("prompt_url", nargs="?", help="声纹参考音频 URL（默认内置 ATRI 声纹）")
parser.add_argument("--text", default="你好，我是一个由IndexTTS-2生成的语音测试。", help="合成文本")
parser.add_argument("--output", default="temp/output/indextts2_test.wav", help="输出路径")
parser.add_argument("--emo-text", help="情感控制文本（如：开心地说、生气地说）")
parser.add_argument("--emo-audio", help="情感参考音频 URL")
parser.add_argument("--emo-alpha", type=float, default=0.5, help="情感强度 0~1（默认0.5）")
args = parser.parse_args()

API_KEY = os.environ.get("GITEE_AI_API_KEY")
if not API_KEY:
    raise ValueError("请将 API Key 写入 .env 文件: GITEE_AI_API_KEY=your_key")

BASE = "https://ai.gitee.com"

prompt_url = args.prompt_url or DEFAULT_PROMPT_URL

audio_dir = Path("voice")
audio_files = list(audio_dir.glob("*.wav"))
prompt_text = audio_files[0].stem if audio_files else "いえ、見えてましたよ。みなさんがいるの。わたし、目がいいので"

extra = {
    "prompt_audio_url": prompt_url,
    "prompt_text": prompt_text,
}

if args.emo_text:
    extra["use_emo_text"] = True
    extra["emo_text"] = args.emo_text

if args.emo_audio:
    extra["emo_audio_prompt_url"] = args.emo_audio
    extra["emo_alpha"] = args.emo_alpha

client = OpenAI(base_url=f"{BASE}/v1", api_key=API_KEY)
response = client.audio.speech.create(
    model="IndexTTS-2",
    input=args.text,
    voice="alloy",
    extra_body=extra,
)

Path("temp/output").mkdir(parents=True, exist_ok=True)
with open(args.output, "wb") as f:
    f.write(response.content)

print(f"语音文件已生成: {args.output}")
print(f"合成文本: {args.text}")
print(f"声纹文本: {prompt_text}")
if args.emo_text:
    print(f"情感文本: {args.emo_text}")
if args.emo_audio:
    print(f"情感音频: {args.emo_audio}")
