import pytest

from atri_indextts.models import TTSRequest, TTSResponse
from atri_indextts.providers.astraflow import AstraFlowProvider
from atri_indextts.providers.gitee import GiteeProvider


class TestGiteeProvider:
    def test_name(self):
        prov = GiteeProvider()
        assert prov.name == "gitee"

    def test_info(self):
        prov = GiteeProvider(api_key="test")
        info = prov.info
        assert info.name == "gitee"
        assert "Atri" in info.available_voices

    def test_list_voices(self):
        prov = GiteeProvider()
        assert "Atri" in prov.list_voices()

    def test_synthesize_missing_api_key_raises(self):
        prov = GiteeProvider(api_key=None)
        with pytest.raises(ValueError, match="未设置 GITEE_AI_API_KEY"):
            prov.synthesize(TTSRequest(text="test"))

    def test_synthesize_without_prompt_audio_raises(self, mocker):
        mock_openai = mocker.patch("atri_indextts.providers.gitee.OpenAI")
        mock_client = mock_openai.return_value
        mock_client.audio.speech.create.return_value.content = b"audio-data"

        prov = GiteeProvider(api_key="test-key")
        with pytest.raises(ValueError, match="请选择声纹预设"):
            prov.synthesize(TTSRequest(text="test", voice=None, prompt_audio=None))

    def test_synthesize_success(self, mocker):
        mock_openai = mocker.patch("atri_indextts.providers.gitee.OpenAI")
        mock_client = mock_openai.return_value
        mock_client.audio.speech.create.return_value.content = b"audio-data"

        prov = GiteeProvider(api_key="test-key")
        response = prov.synthesize(TTSRequest(
            text="hello",
            voice="Atri",
            prompt_index=0,
        ))

        assert isinstance(response, TTSResponse)
        assert response.audio == b"audio-data"
        assert response.format == "wav"


class TestAstraFlowProvider:
    def test_name(self):
        prov = AstraFlowProvider()
        assert prov.name == "astraflow"

    def test_info(self):
        prov = AstraFlowProvider(api_key="test")
        info = prov.info
        assert info.name == "astraflow"
        assert "Atri" in info.available_voices

    def test_list_voices(self):
        prov = AstraFlowProvider()
        assert "Atri" in prov.list_voices()

    def test_synthesize_missing_api_key_raises(self):
        prov = AstraFlowProvider(api_key=None)
        with pytest.raises(ValueError, match="未设置 MODELVERSE_API_KEY"):
            prov.synthesize(TTSRequest(text="test"))

    def test_synthesize_without_prompt_audio_raises(self, mocker):
        mocker.patch(
            "atri_indextts.providers.astraflow.ensure_local_audio",
            return_value=None,
        )
        prov = AstraFlowProvider(api_key="test-key")
        with pytest.raises(ValueError, match="请选择声纹预设"):
            prov.synthesize(TTSRequest(text="test", voice=None, prompt_audio=None))

    def test_synthesize_success(self, tmp_path, mocker):
        fake_audio = tmp_path / "speaker.wav"
        fake_audio.write_bytes(b"\x00\x00")

        mocker.patch(
            "atri_indextts.providers.astraflow.ensure_local_audio",
            return_value=fake_audio,
        )

        prov = AstraFlowProvider(api_key="test-key")
        mock_session = mocker.patch.object(prov, "_session")
        mock_resp = mocker.MagicMock()
        mock_resp.ok = True
        mock_resp.content = b"audio-data"
        mock_session.post = mocker.MagicMock(return_value=mock_resp)

        response = prov.synthesize(TTSRequest(
            text="hello",
            prompt_audio="https://example.com/audio.wav",
        ))

        assert isinstance(response, TTSResponse)
        assert response.audio == b"audio-data"

    def test_synthesize_api_error(self, tmp_path, mocker):
        fake_audio = tmp_path / "speaker.wav"
        fake_audio.write_bytes(b"\x00\x00")

        mocker.patch(
            "atri_indextts.providers.astraflow.ensure_local_audio",
            return_value=fake_audio,
        )

        prov = AstraFlowProvider(api_key="test-key")
        mock_session = mocker.patch.object(prov, "_session")
        mock_resp = mocker.MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.json.return_value = {"error": {"message": "server error"}}
        mock_session.post = mocker.MagicMock(return_value=mock_resp)

        with pytest.raises(ValueError, match="AstraFlow API 错误"):
            prov.synthesize(TTSRequest(
                text="hello",
                prompt_audio="https://example.com/audio.wav",
            ))

    def test_infer_emo_control_method(self):
        assert AstraFlowProvider._infer_emo_control_method(TTSRequest(text="t")) == 0
        assert AstraFlowProvider._infer_emo_control_method(
            TTSRequest(text="t", emo_audio="http://x")
        ) == 1
        assert AstraFlowProvider._infer_emo_control_method(
            TTSRequest(text="t", emo_text="angry")
        ) == 3
