import pytest

import atri_indextts.config


@pytest.fixture(autouse=True)
def _reset_config_cache():
    atri_indextts.config._config_cache = None
