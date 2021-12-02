import os
from wsgiref.simple_server import make_server

import pytest
from wsgidav.wsgidav_app import WsgiDAVApp

from .cloud import AUTH, Webdav
from .httpd import run_server_on_thread


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir), "dvc_webdav", "tests", "docker-compose.yml"
    )


@pytest.fixture
def webdav_server(tmp_path_factory):
    host, port = "localhost", 0
    directory = os.fspath(tmp_path_factory.mktemp("http"))
    dirmap = {"/": directory}

    app = WsgiDAVApp(
        {
            "host": host,
            "port": port,
            "provider_mapping": dirmap,
            "simple_dc": {"user_mapping": {"*": AUTH}},
        }
    )
    server = make_server(host, port, app)
    with run_server_on_thread(server) as httpd:
        yield httpd


@pytest.fixture
def make_webdav(webdav_server):
    def _make_webdav():
        url = Webdav.get_url(webdav_server.server_port)
        return Webdav(url)

    return _make_webdav


@pytest.fixture
def webdav(make_webdav):
    return make_webdav()
