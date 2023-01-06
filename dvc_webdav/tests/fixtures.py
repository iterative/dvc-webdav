import os

import pytest
from cheroot import wsgi
from wsgidav.wsgidav_app import WsgiDAVApp

from .cloud import AUTH, BASE_PATH, Webdav

# pylint: disable=redefined-outer-name


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

    server = wsgi.Server(bind_addr=(host, port), wsgi_app=app)
    with server._run_in_thread():  # pylint: disable=protected-access
        yield server


@pytest.fixture
def make_webdav(webdav_server):
    def _make_webdav():
        url = Webdav.get_url(webdav_server.bind_addr[1])
        return Webdav(url)

    return _make_webdav


@pytest.fixture
def webdav(make_webdav):
    return make_webdav()
