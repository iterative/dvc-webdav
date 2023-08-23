import logging
import threading
from getpass import getpass

from dvc.utils.objects import cached_property
from dvc_objects.fs.base import FileSystem
from funcy import memoize, wrap_prop, wrap_with

logger = logging.getLogger(__name__)


@wrap_with(threading.Lock())
@memoize
def ask_password(host, user):
    return getpass(f"Enter a password for host '{host}' user '{user}':\n")


class WebDAVFileSystem(FileSystem):  # pylint:disable=abstract-method
    protocol = "webdav"
    root_marker = ""
    REQUIRES = {"webdav4": "webdav4"}
    PARAM_CHECKSUM = "etag"

    def __init__(self, **config):
        super().__init__(**config)

        cert_path = config.get("cert_path", None)
        key_path = config.get("key_path", None)
        self.prefix = config.get("prefix", "")
        self.fs_args.update(
            {
                "base_url": config["url"],
                "cert": cert_path if not key_path else (cert_path, key_path),
                "verify": config.get("ssl_verify", True),
                "timeout": config.get("timeout", 30),
            }
        )

    def unstrip_protocol(self, path: str) -> str:
        return self.fs_args["base_url"] + "/" + path

    @staticmethod
    def _get_kwargs_from_urls(urlpath):
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(urlpath)
        scheme = parsed.scheme.replace("webdav", "http")
        return {
            "prefix": parsed.path.rstrip("/"),
            "host": urlunparse((scheme, parsed.netloc, "", None, None, None)),
            "url": urlunparse(
                (
                    scheme,
                    parsed.netloc,
                    parsed.path.rstrip("/"),
                    None,
                    None,
                    None,
                )
            ),
            "user": parsed.username,
        }

    def _prepare_credentials(self, **config):
        user = config.get("user", None)
        password = config.get("password", None)
        headers = {}
        auth = None
        if token := config.get("token"):
            headers.update({"Authorization": f"Bearer {token}"})
        elif user:
            if not password and config.get("ask_password"):
                password = ask_password(config["host"], user)
            auth = (user, password)
        elif custom_auth_header := config.get("custom_auth_header"):
            if not password and config.get("ask_password"):
                password = ask_password(config["host"], custom_auth_header)
            headers.update({custom_auth_header: password})

        return {"headers": headers, "auth": auth}

    @wrap_prop(threading.Lock())
    @cached_property
    def fs(self):
        from webdav4.fsspec import WebdavFileSystem

        return WebdavFileSystem(**self.fs_args)

    def upload_fobj(self, fobj, to_info, **kwargs):
        size = kwargs.get("size")
        # using upload_fileobj to directly upload fileobj rather than buffering
        # and using overwrite=True to avoid check for an extra exists call,
        # as caller should ensure that the file does not exist beforehand.
        return self.fs.upload_fileobj(fobj, to_info, overwrite=True, size=size)


class WebDAVSFileSystem(WebDAVFileSystem):  # pylint:disable=abstract-method
    protocol = "webdavs"
