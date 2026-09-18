import hashlib

from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Document(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        ARCHIVED = 'archived', 'Archived'

    class AccessLevel(models.TextChoices):
        STUDENT = 'student', 'Student'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin'

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        'knowledge.Category',
        on_delete=models.PROTECT,
        related_name='documents',
    )
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.STUDENT,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_documents_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def current_version(self):
        return self.versions.order_by('-version_number').first()


class DocumentVersion(models.Model):
    document = models.ForeignKey(
        'knowledge.Document',
        on_delete=models.CASCADE,
        related_name='versions',
    )
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to='knowledge/documents/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    checksum = models.CharField(max_length=64, blank=True, default='')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_versions_uploaded',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document', '-version_number']
        constraints = [
            models.UniqueConstraint(fields=['document', 'version_number'], name='unique_document_version_number'),
        ]

    def __str__(self):
        return f"{self.document.title} v{self.version_number}"

    def save(self, *args, **kwargs):
        if self.file and not self.checksum:
            self.checksum = self._compute_checksum()
            if hasattr(self.file, 'seek'):
                self.file.seek(0)
        super().save(*args, **kwargs)

    def _compute_checksum(self):
        if not self.file:
            return ''

        file_obj = self.file
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)

        digest = hashlib.sha256()
        while True:
            chunk = file_obj.read(65536)
            if not chunk:
                break
            digest.update(chunk)

        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        return digest.hexdigest()


class DocumentChunk(models.Model):
    document_version = models.ForeignKey(
        'knowledge.DocumentVersion',
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    section = models.CharField(max_length=200, blank=True, default='')
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document_version', 'chunk_index']
        constraints = [
            models.UniqueConstraint(fields=['document_version', 'chunk_index'], name='unique_document_chunk_index'),
        ]

    def __str__(self):
        return f"{self.document_version} chunk {self.chunk_index}"
