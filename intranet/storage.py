import os
from cloudinary.utils import private_download_url
from cloudinary_storage.storage import RawMediaCloudinaryStorage


class SignedRawMediaCloudinaryStorage(RawMediaCloudinaryStorage):
    """
    Storage raw para documentos que utiliza o endpoint de download autenticado da API.
    Isso evita bloqueios de ACL/Segurança que ocorrem na CDN (res.cloudinary.com) 
    para arquivos do tipo 'raw' em contas gratuitas.
    """

    def _get_url(self, name):
        public_id = self._prepend_prefix(name)
        _, ext = os.path.splitext(name)
        file_format = ext.lstrip('.')
        
        # O método private_download_url gera uma URL assinada para o endpoint da API,
        # que é mais robusto para contornar restrições de entrega de PDFs/Raw.
        return private_download_url(
            public_id,
            file_format,
            resource_type=self.RESOURCE_TYPE,
            type="upload",
            attachment=True
        )
