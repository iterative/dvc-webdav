import os

import pytest


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir), "dvc_webdav", "tests", "docker-compose.yml"
    )


@pytest.fixture
def make_webdav():
    def _make_webdav():
        raise NotImplementedError

    return _make_webdav


@pytest.fixture
def webdav(make_webdav):
    return make_webdav()

