from pathlib import Path
from unittest.mock import patch

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.test import SimpleTestCase

from intranet.models import DocumentoRestrito
from intranet.storage import SignedRawMediaCloudinaryStorage
from livraria.models import Livro
from noticias.models import Noticia
from programacao.models import CursoEvento, Doutrinaria
from voluntarios.models import DocumentoVoluntario


class CloudinaryDocumentStorageTests(SimpleTestCase):
    def test_document_models_use_signed_raw_storage(self):
        intranet_storage = DocumentoRestrito._meta.get_field("arquivo").storage
        volunteer_storage = DocumentoVoluntario._meta.get_field("arquivo").storage

        self.assertIsInstance(intranet_storage, SignedRawMediaCloudinaryStorage)
        self.assertIsInstance(volunteer_storage, SignedRawMediaCloudinaryStorage)
        self.assertEqual(intranet_storage.RESOURCE_TYPE, "raw")
        self.assertEqual(volunteer_storage.RESOURCE_TYPE, "raw")

    @patch("intranet.storage.cloudinary_url")
    def test_urls_are_signed_raw_delivery_urls(self, cloudinary_url):
        cloudinary_url.side_effect = [
            ("https://res.cloudinary.test/raw/upload/s--intranet--/sample.pdf", {}),
            ("https://res.cloudinary.test/raw/upload/s--volunteer--/sample.pdf", {}),
        ]

        intranet_storage = DocumentoRestrito._meta.get_field("arquivo").storage
        volunteer_storage = DocumentoVoluntario._meta.get_field("arquivo").storage

        self.assertIn("s--intranet--", intranet_storage.url("intranet_docs/sample.pdf"))
        self.assertIn("s--volunteer--", volunteer_storage.url("voluntarios/historico/sample.pdf"))
        self.assertEqual(cloudinary_url.call_args_list[0].kwargs["resource_type"], "raw")
        self.assertEqual(cloudinary_url.call_args_list[0].kwargs["type"], "upload")
        self.assertTrue(cloudinary_url.call_args_list[0].kwargs["sign_url"])
        self.assertEqual(cloudinary_url.call_args_list[1].kwargs["resource_type"], "raw")
        self.assertEqual(cloudinary_url.call_args_list[1].kwargs["type"], "upload")
        self.assertTrue(cloudinary_url.call_args_list[1].kwargs["sign_url"])

    def test_image_models_keep_the_default_image_storage(self):
        image_fields = (
            (Noticia, "imagem"),
            (Livro, "capa"),
            (CursoEvento, "imagem"),
            (Doutrinaria, "imagem"),
        )

        for model, field_name in image_fields:
            with self.subTest(model=model.__name__, field=field_name):
                storage = model._meta.get_field(field_name).storage
                self.assertIsInstance(storage, MediaCloudinaryStorage)
                self.assertEqual(storage.RESOURCE_TYPE, "image")
                self.assertNotIsInstance(storage, SignedRawMediaCloudinaryStorage)

    def test_download_templates_do_not_apply_image_transformations(self):
        project_root = Path(__file__).resolve().parents[1]
        intranet_item = (
            project_root / "intranet" / "templates" / "intranet" / "includes" / "doc_item.html"
        ).read_text(encoding="utf-8")
        volunteer_item = (
            project_root / "voluntarios" / "templates" / "voluntarios" / "documentos_voluntario.html"
        ).read_text(encoding="utf-8")

        self.assertIn('href="{{ doc.arquivo.url }}" download', intranet_item)
        self.assertIn('href="{{ doc.arquivo.url }}" download', volunteer_item)
        self.assertNotIn("cloudinary_transform", intranet_item)
        self.assertNotIn("cloudinary_transform", volunteer_item)
