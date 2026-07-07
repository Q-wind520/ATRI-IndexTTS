from atri_indextts.voice_loader import get_voice, list_voice_names, load_voices


class TestLoadVoices:
    def test_returns_non_empty_list(self):
        voices = load_voices()
        assert len(voices) >= 1

    def test_voice_has_name_and_prompts(self):
        voices = load_voices()
        atri = voices[0]
        assert atri.name == "Atri"
        assert atri.prompt_count >= 1
        assert atri.prompts[0].label == "日常说话"

    def test_prompt_has_expected_fields(self):
        voices = load_voices()
        prompt = voices[0].prompts[0]
        assert prompt.prompt_audio_url.startswith("https://")
        assert isinstance(prompt.prompt_text, str)
        assert len(prompt.prompt_text) > 0


class TestGetVoice:
    def test_found(self):
        voice = get_voice("Atri")
        assert voice is not None
        assert voice.name == "Atri"

    def test_not_found(self):
        voice = get_voice("Nonexistent")
        assert voice is None


class TestListVoiceNames:
    def test_contains_atri(self):
        names = list_voice_names()
        assert "Atri" in names
