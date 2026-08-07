from cloudinary.utils import cloudinary_url
from cloudinary_storage.storage import RawMediaCloudinaryStorage


class SignedRawMediaCloudinaryStorage(RawMediaCloudinaryStorage):
    """Storage raw da Intranet com URL de entrega assinada pelo Cloudinary."""

    def _get_url(self, name):
        name = self._prepend_prefix(name)
        url, _ = cloudinary_url(
            name,
            resource_type=self.RESOURCE_TYPE,
            type="upload",
            secure=True,
            sign_url=True,
        )
        return url
