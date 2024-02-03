import pytest

from dvc.testing.api_tests import (  # noqa: F401
    TestAPI,
)
from dvc.testing.remote_tests import (  # noqa: F401
    TestRemote,
)
from dvc.testing.workspace_tests import (  # noqa: F401
    TestGetUrl,
    TestImport,
    TestLsUrl,
)


@pytest.fixture
def remote(make_remote):
    return make_remote(name="upstream", typ="webdav")
