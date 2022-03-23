from dvc.testing.cloud import Cloud
from dvc.testing.path_info import WebDAVURLInfo
from funcy import cached_property, first

AUTH = {"user1": {"password": "password1"}}
BASE_PATH = "/dav/files/user1"


class Webdav(Cloud, WebDAVURLInfo):
    @staticmethod
    def get_url(port):  # pylint: disable=arguments-differ
        return f"webdav://localhost:{port}{BASE_PATH}"

    @property
    def config(self):
        user, secrets = first(AUTH.items())
        url = f"webdav://{self.netloc}{self._spath}"
        return {"url": url, "user": user, **secrets}

    @cached_property
    def client(self):
        from webdav4.client import Client

        user, secrets = first(AUTH.items())
        return Client(
            self.replace(path=BASE_PATH).url, auth=(user, secrets["password"])
        )

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        assert mode == 0o777
        parent_dirs = list(reversed(self.parents))[1:] if parents else []
        for d in parent_dirs + [self]:
            path = d.path  # pylint: disable=no-member
            if not self.client.exists(path):
                self.client.mkdir(path)

    def write_bytes(self, contents):
        from io import BytesIO

        self.client.upload_fileobj(BytesIO(contents), self.path)

    @property
    def fs_path(self):
        return self.path.lstrip("/")

    def exists(self):
        raise NotImplementedError

    def is_dir(self):
        raise NotImplementedError

    def is_file(self):
        raise NotImplementedError

    def read_bytes(self):
        raise NotImplementedError
