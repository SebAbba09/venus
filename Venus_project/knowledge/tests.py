from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from users.models import User

from .models import Category, Document, DocumentChunk, DocumentVersion


class KnowledgeModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='demo_user', password='A secure password 123!')
        self.category = Category.objects.create(
            name='DEMO - Administrative',
            slug='demo-administrative',
            description='Données de démonstration.',
        )

    def test_category_creation_and_uniqueness(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(str(self.category), 'DEMO - Administrative')

        with self.assertRaises(Exception):
            Category.objects.create(name='DEMO - Administrative', slug='demo-admin-2')

        with self.assertRaises(Exception):
            Category.objects.create(name='DEMO - New', slug='demo-administrative')

    def test_document_creation_and_relations(self):
        document = Document.objects.create(
            title='DEMO - Document test',
            description='Document de démonstration.',
            category=self.category,
            access_level=Document.AccessLevel.STUDENT,
            status=Document.Status.ACTIVE,
            created_by=self.user,
        )

        self.assertEqual(str(document), 'DEMO - Document test')
        self.assertEqual(document.category, self.category)
        self.assertEqual(document.status, Document.Status.ACTIVE)
        self.assertEqual(document.access_level, Document.AccessLevel.STUDENT)

    def test_document_versions_are_versioned_per_document(self):
        document = Document.objects.create(
            title='DEMO - Versioned doc',
            category=self.category,
            created_by=self.user,
        )

        file_one = SimpleUploadedFile('demo-v1.txt', b'premiere version', content_type='text/plain')
        version_one = DocumentVersion.objects.create(
            document=document,
            version_number=1,
            file=file_one,
            original_filename='demo-v1.txt',
            uploaded_by=self.user,
        )

        file_two = SimpleUploadedFile('demo-v2.txt', b'deuxieme version', content_type='text/plain')
        version_two = DocumentVersion.objects.create(
            document=document,
            version_number=2,
            file=file_two,
            original_filename='demo-v2.txt',
            uploaded_by=self.user,
        )

        self.assertEqual(document.versions.count(), 2)
        self.assertEqual(version_one.version_number, 1)
        self.assertEqual(version_two.version_number, 2)
        self.assertTrue(version_one.checksum)
        self.assertTrue(version_two.checksum)

    def test_document_version_number_is_unique_per_document(self):
        document = Document.objects.create(
            title='DEMO - Unique version',
            category=self.category,
            created_by=self.user,
        )

        DocumentVersion.objects.create(
            document=document,
            version_number=1,
            file=SimpleUploadedFile('demo.txt', b'abc', content_type='text/plain'),
            original_filename='demo.txt',
            uploaded_by=self.user,
        )

        with self.assertRaises(Exception):
            DocumentVersion.objects.create(
                document=document,
                version_number=1,
                file=SimpleUploadedFile('demo-2.txt', b'def', content_type='text/plain'),
                original_filename='demo-2.txt',
                uploaded_by=self.user,
            )

    def test_document_chunk_creation_and_constraints(self):
        document = Document.objects.create(
            title='DEMO - Chunked doc',
            category=self.category,
            created_by=self.user,
        )
        version = DocumentVersion.objects.create(
            document=document,
            version_number=1,
            file=SimpleUploadedFile('demo.txt', b'chunk content', content_type='text/plain'),
            original_filename='demo.txt',
            uploaded_by=self.user,
        )

        chunk_one = DocumentChunk.objects.create(
            document_version=version,
            chunk_index=0,
            content='Premier chunk.',
            page_number=1,
            section='Introduction',
            metadata={'source': 'demo'},
        )
        chunk_two = DocumentChunk.objects.create(
            document_version=version,
            chunk_index=1,
            content='Second chunk.',
            page_number=2,
            section='Règlement',
            metadata={'source': 'demo'},
        )

        self.assertEqual(version.chunks.count(), 2)
        self.assertEqual(str(chunk_one), f'{version} chunk 0')
        self.assertEqual(chunk_two.page_number, 2)
        self.assertEqual(chunk_two.section, 'Règlement')

    def test_document_version_file_stays_local_and_not_on_e_drive(self):
        document = Document.objects.create(
            title='DEMO - Media path',
            category=self.category,
            created_by=self.user,
        )
        version = DocumentVersion.objects.create(
            document=document,
            version_number=1,
            file=SimpleUploadedFile('demo.txt', b'content', content_type='text/plain'),
            original_filename='demo.txt',
            uploaded_by=self.user,
        )

        self.assertIn('knowledge/documents', version.file.name)
        self.assertNotIn('E:', version.file.name)
        self.assertNotIn('e:', version.file.name.lower())

    def test_chunk_index_is_unique_for_same_version(self):
        document = Document.objects.create(
            title='DEMO - Duplicate chunk check',
            category=self.category,
            created_by=self.user,
        )
        version = DocumentVersion.objects.create(
            document=document,
            version_number=1,
            file=SimpleUploadedFile('demo.txt', b'content', content_type='text/plain'),
            original_filename='demo.txt',
            uploaded_by=self.user,
        )

        DocumentChunk.objects.create(
            document_version=version,
            chunk_index=0,
            content='A',
        )

        with self.assertRaises(Exception):
            DocumentChunk.objects.create(
                document_version=version,
                chunk_index=0,
                content='B',
            )
