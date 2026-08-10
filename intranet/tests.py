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

    @patch("intranet.storage.private_download_url")
    def test_urls_are_authenticated_download_urls(self, private_download_url):
        private_download_url.side_effect = [
            "https://api.cloudinary.test/v1_1/demo/raw/download?public_id=intranet&signature=s1",
            "https://api.cloudinary.test/v1_1/demo/raw/download?public_id=volunteer&signature=s2",
        ]

        intranet_storage = DocumentoRestrito._meta.get_field("arquivo").storage
        volunteer_storage = DocumentoVoluntario._meta.get_field("arquivo").storage

        self.assertIn("signature=s1", intranet_storage.url("intranet_docs/sample.pdf"))
        self.assertIn("signature=s2", volunteer_storage.url("voluntarios/historico/sample.pdf"))
        self.assertEqual(private_download_url.call_args_list[0].args[0], "media/intranet_docs/sample.pdf")
        self.assertEqual(private_download_url.call_args_list[0].kwargs["resource_type"], "raw")
        self.assertEqual(private_download_url.call_args_list[0].kwargs["type"], "upload")
        self.assertTrue(private_download_url.call_args_list[0].kwargs["attachment"])

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

    def test_term_generation_includes_date_tags(self):
        project_root = Path(__file__).resolve().parents[1]
        views_content = (project_root / "voluntarios" / "views.py").read_text(encoding="utf-8")
        
        self.assertIn("context_dict['dia'] = hoje.strftime", views_content)
        self.assertIn("context_dict['mes_nome'] = meses[hoje.month]", views_content)
        self.assertIn("context_dict['ano'] = hoje.strftime", views_content)
        self.assertIn("'Janeiro'", views_content)
        self.assertIn("'Dezembro'", views_content)
