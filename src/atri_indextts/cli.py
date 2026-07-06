import sys
from io import TextIOWrapper

import click

if isinstance(sys.stdout, TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

from .service import TTSService


@click.group()
def cli():
    """ATRI-IndexTTS — 统一 IndexTTS 模型 API 服务商接口"""


@cli.command()
@click.argument("text")
@click.option("-p", "--provider", default=None, help="服务商标识")
@click.option("-v", "--voice", default=None, help="语音角色 (可用的命令: indextts voices)")
@click.option("-o", "--output", default=None, help="输出文件路径 (默认: temp/output/indextts.wav)")
@click.option("--prompt-audio", default=None, help="声纹参考音频 URL")
@click.option("--prompt-text", default=None, help="声纹参考文本")
@click.option("--emo-audio", default=None, help="音频控制语气参考音频")
@click.option("--emo-alpha", default=None, type=float, help="音频控制语气影响强度 0~1 (使用 --emo-audio 时默认为 0.5)")
@click.option("--emo-text", default=None, help="文本控制语气参考语句")
@click.option("--prompt-index", default=0, type=int, help="参考声纹编号 (可用: indextts voices 查看)")
def tts(text, provider, voice, output, prompt_audio, prompt_text, emo_audio, emo_alpha, emo_text, prompt_index):
    """文本转语音合成"""
    service = TTSService()
    try:
        out_path = service.synthesize(
            text=text,
            provider=provider,
            voice=voice,
            output=output,
            prompt_audio=prompt_audio,
            prompt_text=prompt_text,
            emo_audio=emo_audio,
            emo_alpha=emo_alpha,
            emo_text=emo_text,
            prompt_index=prompt_index,
        )
        click.echo(f"语音文件已生成: {out_path}")
    except ValueError as e:
        raise click.UsageError(str(e)) from e


@cli.command()
def voices():
    """列出所有可用语音角色"""
    service = TTSService()
    voice_list = service.list_voices()
    click.echo("可用音色:")
    for voice in voice_list:
        click.echo(f"  {voice.name} ({voice.prompt_count} 参考声纹)")
        for i, prompt in enumerate(voice.prompts):
            label = prompt.label or "(无标签)"
            desc = f" — {prompt.description}" if prompt.description else ""
            click.echo(f"    [{i}] {label}{desc}")


@cli.command()
def providers():
    """列出已配置的服务商"""
    service = TTSService()
    data = service.list_providers()
    click.echo("已配置服务商:")
    for name, details in data["providers"].items():
        marker = " [默认]" if name == data["default"] else ""
        click.echo(f"  - {name}{marker}")
        click.echo(f"    base_url: {details['base_url']}")


@cli.group()
def config():
    """管理配置"""


@config.command("show")
def config_show():
    """显示当前配置"""
    service = TTSService()
    data = service.get_config()

    default = data["default_provider"]
    if default:
        click.echo(f"default_provider: {default}")
    else:
        click.echo("default_provider: (未设置)")
    click.echo("providers:")
    for name, details in data["providers"].items():
        click.echo(f"  {name}:")
        click.echo(f"    base_url: {details.get('base_url', 'N/A')}")
        api_key = data["api_keys"].get(name)
        click.echo(f"    api_key: {api_key if api_key else '(未设置)'}")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """设置配置项 (provider.base_url 或 default_provider)"""
    service = TTSService()
    try:
        service.set_config(key, value)
        click.echo(f"{key} 已设为: {value}")
    except ValueError as e:
        raise click.UsageError(str(e)) from e


def main():
    cli()


if __name__ == "__main__":
    main()
