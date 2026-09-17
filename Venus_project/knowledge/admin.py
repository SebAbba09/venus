from django.contrib import admin

from .models import Category, Document, DocumentChunk, DocumentVersion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)
    ordering = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'access_level', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('status', 'access_level', 'category')
    ordering = ('title',)


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'original_filename', 'checksum', 'created_at')
    search_fields = ('document__title', 'original_filename', 'checksum')
    list_filter = ('document__category',)
    ordering = ('document__title', '-version_number')


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document_version', 'chunk_index', 'page_number', 'section')
    search_fields = ('content', 'section')
    list_filter = ('document_version__document__category', 'page_number')
    ordering = ('document_version__document__title', 'chunk_index')
