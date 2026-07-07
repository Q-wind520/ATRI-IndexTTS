import json
import os

from atri_indextts.config import (
    DEFAULT_CONFIG,
    get_api_key,
    load_config,
    load_env,
    reload_config,
    save_config,
)


class TestLoadConfig:
    def test_returns_default_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)

        result = load_config()
        assert result == DEFAULT_CONFIG

    def test_reads_existing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        config_data = {"default_provider": "gitee", "providers": {}}
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_data), encoding="utf-8")

        result = load_config()
        assert result["default_provider"] == "gitee"

    def test_handles_invalid_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        (tmp_path / "config.json").write_text("{invalid", encoding="utf-8")

        result = load_config()
        assert result == DEFAULT_CONFIG

    def test_cache_avoids_reread(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        config_path = tmp_path / "config.json"
        config_path.write_text('{"default_provider": "gitee"}', encoding="utf-8")

        load_config()
        config_path.write_text('{"default_provider": "astraflow"}', encoding="utf-8")

        result = load_config()
        assert result["default_provider"] == "gitee"


class TestSaveConfig:
    def test_writes_file_and_updates_cache(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        config_data = {"default_provider": "astraflow", "providers": {}}

        save_config(config_data)

        written = json.loads((tmp_path / "config.json").read_text(encoding="utf-8"))
        assert written["default_provider"] == "astraflow"

        cached = load_config()
        assert cached["default_provider"] == "astraflow"


class TestReloadConfig:
    def test_clears_cache_and_reloads(self, tmp_path, monkeypatch):
        monkeypatch.setattr("atri_indextts.config._config_dir", lambda: tmp_path)
        config_path = tmp_path / "config.json"
        config_path.write_text('{"default_provider": "gitee"}', encoding="utf-8")

        load_config()
        config_path.write_text('{"default_provider": "astraflow"}', encoding="utf-8")

        assert load_config()["default_provider"] == "gitee"

        result = reload_config()
        assert result["default_provider"] == "astraflow"


class TestGetApiKey:
    def test_returns_key_from_env(self, monkeypatch):
        monkeypatch.setenv("GITEE_AI_API_KEY", "test-key")
        assert get_api_key("gitee") == "test-key"

    def test_returns_none_for_unknown_provider(self):
        assert get_api_key("nonexistent") is None

    def test_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("GITEE_AI_API_KEY", raising=False)
        assert get_api_key("gitee") is None


class TestLoadEnv:
    def test_reads_env_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("GITEE_AI_API_KEY=mykey\n# comment\nMODELVERSE_API_KEY=otherkey\n", encoding="utf-8")

        load_env(str(env_file))

        assert os.environ["GITEE_AI_API_KEY"] == "mykey"
        assert os.environ["MODELVERSE_API_KEY"] == "otherkey"

    def test_does_not_overwrite_existing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GITEE_AI_API_KEY", "existing")
        env_file = tmp_path / ".env"
        env_file.write_text("GITEE_AI_API_KEY=newvalue", encoding="utf-8")

        load_env(str(env_file))

        assert os.environ["GITEE_AI_API_KEY"] == "existing"

    def test_no_error_when_file_missing(self):
        load_env("nonexistent_file.env")
