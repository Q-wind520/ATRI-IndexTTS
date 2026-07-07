from pathlib import Path

import pytest

from atri_indextts.models import TTSRequest
from atri_indextts.service import TTSService


class TestGetProviderName:
    def test_from_argument(self):
        service = TTSService()
        assert service._get_provider_name("gitee") == "gitee"

    def test_from_default_config(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        from atri_indextts.config import CONFIG_FILENAME, reload_config
        import json
        (tmp_path / CONFIG_FILENAME).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / CONFIG_FILENAME).write_text(
            json.dumps({"default_provider": "astraflow", "providers": {}}),
            encoding="utf-8",
        )
        reload_config()

        service = TTSService()
        assert service._get_provider_name(None) == "astraflow"

    def test_raises_when_missing(self):
        service = TTSService()
        with pytest.raises(ValueError, match="请指定服务商"):
            service._get_provider_name(None)


class TestResolveProvider:
    def test_valid_gitee(self):
        service = TTSService()
        prov = service._resolve_provider("gitee")
        assert prov.name == "gitee"

    def test_valid_astraflow(self):
        service = TTSService()
        prov = service._resolve_provider("astraflow")
        assert prov.name == "astraflow"

    def test_unknown_raises(self):
        service = TTSService()
        with pytest.raises(ValueError, match="未知服务商"):
            service._resolve_provider("unknown")


class TestSynthesize:
    def test_synthesize_with_mock_provider(self, mocker, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: Path("nonexistent"))
        mock_provider = mocker.MagicMock()
        mock_provider.synthesize.return_value = mocker.MagicMock(audio=b"fake-audio", format="wav")
        mocker.patch.object(TTSService, "_resolve_provider", return_value=mock_provider)

        service = TTSService()
        result = service.synthesize(text="hello", provider="gitee", output="tmp/test.wav")

        assert result == Path("tmp/test.wav")
        mock_provider.synthesize.assert_called_once()
        request: TTSRequest = mock_provider.synthesize.call_args[0][0]
        assert request.text == "hello"

    def test_default_output_path(self, mocker, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: Path("nonexistent"))
        mock_provider = mocker.MagicMock()
        mock_provider.synthesize.return_value = mocker.MagicMock(audio=b"fake-audio", format="wav")
        mocker.patch.object(TTSService, "_resolve_provider", return_value=mock_provider)

        service = TTSService()
        result = service.synthesize(text="hello", provider="gitee")

        assert result == Path("temp/output/indextts.wav")


class TestListVoices:
    def test_returns_voice_list(self):
        service = TTSService()
        voices = service.list_voices()
        assert len(voices) >= 1
        assert voices[0].name == "Atri"


class TestListProviders:
    def test_returns_dict(self):
        service = TTSService()
        result = service.list_providers()
        assert "default" in result
        assert "providers" in result
        assert "gitee" in result["providers"]


class TestGetConfig:
    def test_includes_api_keys_masked(self):
        service = TTSService()
        config = service.get_config()
        assert "api_keys" in config
        assert "gitee" in config["api_keys"]


class TestSetConfig:
    def test_sets_default_provider(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        from atri_indextts.config import load_config

        service = TTSService()
        service.set_config("default_provider", "astraflow")

        config = load_config()
        assert config["default_provider"] == "astraflow"

    def test_sets_provider_base_url(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        from atri_indextts.config import load_config

        service = TTSService()
        service.set_config("gitee.base_url", "https://custom.example.com/v1")

        config = load_config()
        assert config["providers"]["gitee"]["base_url"] == "https://custom.example.com/v1"

    def test_unknown_key_raises(self):
        service = TTSService()
        with pytest.raises(ValueError, match="未知配置项"):
            service.set_config("unknown_key", "value")
