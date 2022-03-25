import os
import threading
from wsgiref.simple_server import make_server

import pytest
from wsgidav.wsgidav_app import WsgiDAVApp

from .cloud import AUTH, BASE_PATH, Webdav


@pytest.fixture
def webdav_server(tmp_path_factory):
    host, port = "localhost", 0
    directory = os.fspath(tmp_path_factory.mktemp("http"))
    dirmap = {BASE_PATH: directory}

    app = WsgiDAVApp(
        {
            "host": host,
            "port": port,
            "provider_mapping": dirmap,
            "simple_dc": {"user_mapping": {"*": AUTH}},
        }
    )
    with make_server(host, port, app) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        yield server


@pytest.fixture
def make_webdav(webdav_server):
    def _make_webdav():
        url = Webdav.get_url(webdav_server.server_port)
        return Webdav(url)

    return _make_webdav


@pytest.fixture
def webdav(make_webdav):
    return make_webdav()
