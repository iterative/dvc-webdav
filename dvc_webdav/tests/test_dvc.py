import pytest
from dvc.testing.api_tests import (  # noqa, pylint: disable=unused-import
    TestAPI,
)
from dvc.testing.remote_tests import (  # noqa, pylint: disable=unused-import
    TestRemote,
)


@pytest.fixture(autouse=True)
def mocked_odb(mocker):
    from dvc_objects.db import ObjectDB

    oinit = ObjectDB._init

    def init(self, *args, **kwargs):
        if self.fs.protocol != "webdav":
            return oinit(self, *args, **kwargs)

    yield mocker.patch.object(ObjectDB, "_init", init)


@pytest.fixture
def remote(make_remote):
    yield make_remote(name="upstream", typ="webdav")
