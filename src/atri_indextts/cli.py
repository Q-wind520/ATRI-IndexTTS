import sys
from pathlib import Path

import click

sys.stdout.reconfigure(encoding="utf-8")

from .config import DEFAULT_CONFIG, get_api_key, load_config, load_env, save_config
from .models import TTSRequest
from .providers import GiteeProvider


def _resolve_provider(name: str):
    if name == "gitee":
        api_key = get_api_key("gitee")
        if not api_key:
            raise click.UsageError(
                "未设置 GITEE_AI_API_KEY，请在 .env 中配置"
            )
        config = load_config()
        base_url = config.get("providers", {}).get("gitee", {}).get("base_url", GiteeProvider.BASE_URL)
        return GiteeProvider(api_key=api_key, base_url=base_url)
    raise click.UsageError(f"未知服务商: {name}")


@click.group()
def cli():
    """ATRI-IndexTTS — 统一 IndexTTS 模型 API 服务商接口"""


@cli.command()
@click.argument("text")
@click.option("-p", "--provider", default=None, help="服务商标识 (默认从配置文件读取)")
@click.option("-v", "--voice", default="Atri", help="语音角色 (默认: Atri)")
@click.option("-o", "--output", default=None, help="输出文件路径 (默认: temp/output/indextts.wav)")
@click.option("--prompt-audio", default=None, help="声纹参考音频 URL")
@click.option("--prompt-text", default=None, help="声纹参考文本")
def tts(text, provider, voice, output, prompt_audio, prompt_text):
    """文本转语音合成"""
    load_env()
    config = load_config()

    if provider is None:
        provider = config.get("default_provider", "gitee")

    prov = _resolve_provider(provider)

    if output is None:
        output = "temp/output/indextts.wav"

    request = TTSRequest(
        text=text,
        voice=voice,
        prompt_audio=prompt_audio,
        prompt_text=prompt_text,
        provider=provider,
    )

    response = prov.synthesize(request)

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(response.audio)

    click.echo(f"语音文件已生成: {out_path}")


@cli.command()
@click.option("-p", "--provider", default=None, help="服务商标识")
def voices(provider):
    """列出可用语音角色"""
    load_env()
    config = load_config()

    if provider is None:
        provider = config.get("default_provider", "gitee")

    prov = _resolve_provider(provider)
    voice_list = prov.list_voices()

    click.echo(f"服务商 [{provider}] 可用语音:")
    for v in voice_list:
        click.echo(f"  - {v}")


@cli.command()
def providers():
    """列出已配置的服务商"""
    load_env()
    config = load_config()

    default = config.get("default_provider", "gitee")
    click.echo("已配置服务商:")

    for name, details in config.get("providers", {}).items():
        marker = " [默认]" if name == default else ""
        click.echo(f"  - {name}{marker}")
        click.echo(f"    base_url: {details.get('base_url', 'N/A')}")


@cli.group()
def config():
    """管理配置"""


@config.command("show")
def config_show():
    """显示当前配置"""
    load_env()
    config_data = load_config()

    api_keys = {}
    for provider in config_data.get("providers", {}):
        key = get_api_key(provider)
        api_keys[provider] = "***" if key else "(未设置)"

    click.echo(f"default_provider: {config_data.get('default_provider', 'gitee')}")
    click.echo("providers:")
    for name, details in config_data.get("providers", {}).items():
        click.echo(f"  {name}:")
        click.echo(f"    base_url: {details.get('base_url', 'N/A')}")
        click.echo(f"    api_key: {api_keys.get(name, '(未设置)')}")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """设置配置项 (provider.base_url 或 default_provider)"""
    config_data = load_config()

    if key == "default_provider":
        config_data["default_provider"] = value
        save_config(config_data)
        click.echo(f"default_provider 已设为: {value}")
    elif "." in key:
        provider, field = key.split(".", 1)
        if provider not in config_data.get("providers", {}):
            config_data.setdefault("providers", {})[provider] = {}
        config_data["providers"][provider][field] = value
        save_config(config_data)
        click.echo(f"{provider}.{field} 已设为: {value}")
    else:
        raise click.UsageError(f"未知配置项: {key}，支持: default_provider, <provider>.base_url")


def main():
    load_env()
    cli()


if __name__ == "__main__":
    main()
