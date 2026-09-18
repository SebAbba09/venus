import re
from io import BytesIO
from pathlib import Path
from typing import Protocol, Sequence, TypeVar

from django.db import transaction

from .models import DocumentChunk, DocumentVersion


class DocumentIngestionError(Exception):
    pass


class UnsupportedFileTypeError(DocumentIngestionError):
    pass


class MissingDocumentFileError(DocumentIngestionError):
    pass


class EmptyDocumentError(DocumentIngestionError):
    pass


class NoTextExtractedError(DocumentIngestionError):
    pass


class InvalidDocumentError(DocumentIngestionError):
    pass


Token = TypeVar('Token')


class TokenCounter(Protocol[Token]):
    def tokenize(self, text: str) -> Sequence[Token]:
        ...

    def detokenize(self, tokens: Sequence[Token]) -> str:
        ...


class WhitespaceTokenCounter:
    """Deterministic local adapter used until a model tokenizer is selected."""

    def tokenize(self, text: str) -> Sequence[str]:
        return text.split()

    def detokenize(self, tokens: Sequence[str]) -> str:
        return ' '.join(tokens)


def normalize_text(text: str) -> str:
    if text is None:
        return ''
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[\t\f\v]+', ' ', text)
    text = re.sub(r'[ \t]*\n[ \t]*', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    text = re.sub(r' +\n', '\n', text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
    token_counter: TokenCounter | None = None,
):
    cleaned = normalize_text(text)
    if not cleaned:
        return []

    if chunk_size <= 0:
        raise ValueError('chunk_size must be greater than zero')
    if overlap < 0:
        raise ValueError('overlap cannot be negative')
    if overlap >= chunk_size:
        raise ValueError('overlap must be smaller than chunk_size')

    counter = token_counter or WhitespaceTokenCounter()
    tokens = list(counter.tokenize(cleaned))
    if len(tokens) <= chunk_size:
        return [counter.detokenize(tokens)]

    step = max(1, chunk_size - overlap)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(len(tokens), start + chunk_size)
        chunk = counter.detokenize(tokens[start:end])
        if chunk:
            chunks.append(chunk)
        if end == len(tokens):
            break
        start += step
    return chunks


def _read_file_source(file_source):
    if hasattr(file_source, 'read'):
        if hasattr(file_source, 'seek'):
            file_source.seek(0)
        content = file_source.read()
        if hasattr(file_source, 'seek'):
            file_source.seek(0)
        return content
    with open(file_source, 'rb') as handle:
        return handle.read()


def _extract_pdf_text(file_source):
    try:
        import fitz
    except ImportError as exc:
        raise InvalidDocumentError('PyMuPDF is not available.') from exc

    try:
        doc = fitz.open(stream=_read_file_source(file_source), filetype='pdf')
    except Exception as exc:
        raise InvalidDocumentError('PDF file is invalid or unreadable.') from exc

    try:
        pages = []
        for page_number, page in enumerate(doc, start=1):
            try:
                text = page.get_text('text')
            except Exception as exc:
                raise InvalidDocumentError('PDF file is invalid or unreadable.') from exc
            if text and text.strip():
                pages.append({
                    'page_number': page_number,
                    'section': '',
                    'text': normalize_text(text),
                })
        if not pages:
            raise NoTextExtractedError('PDF file contains no usable text.')
        return pages
    finally:
        doc.close()


def _extract_docx_text(file_source):
    try:
        from docx import Document
    except ImportError as exc:
        raise InvalidDocumentError('python-docx is not available.') from exc

    try:
        document = Document(BytesIO(_read_file_source(file_source)))
    except Exception as exc:
        raise InvalidDocumentError('DOCX file is invalid or unreadable.') from exc

    pages = []
    current_section = ''
    current_paragraphs = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        style_name = paragraph.style.name.lower() if paragraph.style and paragraph.style.name else ''
        if style_name.startswith('heading'):
            if current_paragraphs:
                pages.append({
                    'page_number': None,
                    'section': current_section,
                    'text': normalize_text('\n'.join(current_paragraphs)),
                })
                current_paragraphs = []
            current_section = text
            continue
        current_paragraphs.append(text)

    if current_paragraphs:
        pages.append({
            'page_number': None,
            'section': current_section,
            'text': normalize_text('\n'.join(current_paragraphs)),
        })

    if not pages:
        raise NoTextExtractedError('DOCX file contains no usable text.')
    return pages


def _extract_txt_text(file_source):
    try:
        text = _read_file_source(file_source).decode('utf-8')
    except UnicodeDecodeError as exc:
        raise InvalidDocumentError('TXT file is not valid UTF-8 text.') from exc
    except OSError as exc:
        raise InvalidDocumentError('TXT file is unreadable.') from exc

    normalized = normalize_text(text)
    if not normalized:
        raise EmptyDocumentError('TXT file is empty.')
    return [{'page_number': None, 'section': '', 'text': normalized}]


def extract_document_text(file_source, extension: str):
    file_ext = (extension or '').lower()
    if file_ext == '.pdf':
        return _extract_pdf_text(file_source)
    if file_ext == '.docx':
        return _extract_docx_text(file_source)
    if file_ext == '.txt':
        return _extract_txt_text(file_source)
    raise UnsupportedFileTypeError(f'Unsupported file type: {extension or "unknown"}')


def ingest_document_version(
    document_version: DocumentVersion,
    chunk_size: int = 800,
    overlap: int = 120,
    token_counter: TokenCounter | None = None,
):
    if document_version is None:
        raise MissingDocumentFileError('Document version is required.')
    if not document_version.file or not document_version.file.name:
        raise MissingDocumentFileError('Document version file is missing.')

    extension = Path(document_version.file.name).suffix.lower()
    if not extension:
        raise UnsupportedFileTypeError('File extension is missing.')

    try:
        with document_version.file.open('rb') as file_handle:
            extracted_pages = extract_document_text(file_handle, extension)
    except FileNotFoundError as exc:
        raise MissingDocumentFileError('Document file does not exist on disk.') from exc
    except OSError as exc:
        raise InvalidDocumentError('Document file is unreadable.') from exc
    if not extracted_pages:
        raise NoTextExtractedError('No text could be extracted from the document.')

    chunks = []
    for page in extracted_pages:
        text = normalize_text(page.get('text', ''))
        if not text:
            continue
        split_chunks = chunk_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
            token_counter=token_counter,
        )
        for index, chunk in enumerate(split_chunks):
            chunk_number = len(chunks)
            chunks.append({
                'chunk_index': chunk_number,
                'content': chunk,
                'page_number': page.get('page_number'),
                'section': page.get('section', ''),
                'metadata': {
                    'source_type': extension.lstrip('.'),
                    'page_number': page.get('page_number'),
                    'section': page.get('section', ''),
                    'chunk_size': chunk_size,
                    'overlap': overlap,
                },
            })

    if not chunks:
        raise EmptyDocumentError('Document contains no usable text after normalization.')

    with transaction.atomic():
        document_version.chunks.all().delete()

        created_chunks = []
        for chunk in chunks:
            created_chunks.append(
                DocumentChunk.objects.create(
                    document_version=document_version,
                    chunk_index=chunk['chunk_index'],
                    content=chunk['content'],
                    page_number=chunk['page_number'],
                    section=chunk['section'],
                    metadata=chunk['metadata'],
                )
            )
    return created_chunks
