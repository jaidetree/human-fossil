"""Media storage backend for R2."""

import mimetypes
from typing import Any

from storages.backends.s3 import S3Storage


class ExtensionTypedS3Storage(S3Storage):
    """Label objects by file extension rather than by the upload's sniffed type.

    ``ImageField`` uploads carry Pillow's detected MIME type, which django-storages
    prefers over the extension. Camera JPEGs with Multi-Picture data are detected
    as ``image/mpo``, which browsers download instead of displaying. The extension
    is already normalized by the ``*_upload_to`` functions, so trust it; fall
    back to the upload's own type only when the extension is unknown.
    """

    def _get_write_parameters(self, name: str, content: Any = None) -> dict[str, Any]:
        params = super()._get_write_parameters(name, content)
        guessed, _encoding = mimetypes.guess_type(name)
        if guessed:
            params["ContentType"] = guessed
        return params
