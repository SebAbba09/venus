from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
CORPUS_DIR = ROOT_DIR / 'experiments' / 'embeddings' / 'corpus'
SOURCE_PATH = CORPUS_DIR / 'corpus.jsonl'
SOURCE_MANIFEST_PATH = CORPUS_DIR / 'manifest.json'
CHUNKS_PATH = CORPUS_DIR / 'chunks.jsonl'
CHUNKS_MANIFEST_PATH = CORPUS_DIR / 'chunks_manifest.json'

CHUNK_SIZE = 400
OVERLAP = 50

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Venus_project.settings')

import django

django.setup()

from knowledge.services import WhitespaceTokenCounter, chunk_text, normalize_text


def load_corpus(path: Path = SOURCE_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f'Corpus not found: {path}')

    records = []
    with path.open('r', encoding='utf-8') as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSONL at line {line_number}.') from exc
            if not isinstance(record, dict):
                raise ValueError(f'Corpus line {line_number} must contain a JSON object.')
            records.append(record)
    return records


def _validate_parameters(chunk_size: int, overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError('chunk_size must be greater than zero')
    if overlap < 0:
        raise ValueError('overlap cannot be negative')
    if overlap >= chunk_size:
        raise ValueError('overlap must be smaller than chunk_size')


def _source_id(record: dict[str, Any]) -> str:
    value = record.get('source_id', record.get('id'))
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Document is missing source_id.')
    return value.strip()


def build_chunks(
    records: list[dict[str, Any]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = OVERLAP,
) -> list[dict[str, Any]]:
    _validate_parameters(chunk_size, overlap)
    counter = WhitespaceTokenCounter()
    chunks = []
    seen_ids = set()

    for record in records:
        source_id = _source_id(record)
        content = normalize_text(record.get('content', ''))
        if not content:
            raise ValueError(f'Document {source_id} has no usable content.')

        document_chunks = chunk_text(
            content,
            chunk_size=chunk_size,
            overlap=overlap,
            token_counter=counter,
        )
        for index, chunk_content in enumerate(document_chunks, start=1):
            if not chunk_content.strip():
                raise ValueError(f'Document {source_id} produced an empty chunk.')
            chunk_id = f'{source_id}_C{index:03d}'
            if chunk_id in seen_ids:
                raise ValueError(f'Duplicate chunk_id: {chunk_id}')
            seen_ids.add(chunk_id)
            chunks.append(
                {
                    'chunk_id': chunk_id,
                    'source_id': source_id,
                    'chunk_index': index,
                    'title': record.get('title', ''),
                    'category': record.get('category', ''),
                    'url': record.get('url', ''),
                    'capture_date': record.get('capture_date', record.get('captured_at', '')),
                    'content': chunk_content,
                    'unit_count': len(counter.tokenize(chunk_content)),
                }
            )
    return chunks


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open('w', encoding='utf-8', newline='\n') as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write('\n')


def build_manifest(
    records: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    source_path: Path = SOURCE_PATH,
) -> dict[str, Any]:
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    return {
        'schema_version': '1.0',
        'source_corpus': 'corpus.jsonl',
        'source_manifest': 'manifest.json',
        'source_sha256': source_hash,
        'document_count': len(records),
        'chunk_count': len(chunks),
        'chunking': {
            'strategy': 'token_aware',
            'chunk_size': CHUNK_SIZE,
            'overlap': OVERLAP,
            'counter': 'whitespace',
            'counter_is_model_tokenizer': False,
        },
    }


def main() -> None:
    records = load_corpus()
    chunks = build_chunks(records)
    manifest = build_manifest(records, chunks)
    _write_jsonl(CHUNKS_PATH, chunks)
    with CHUNKS_MANIFEST_PATH.open('w', encoding='utf-8', newline='\n') as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')

    print('=' * 72)
    print('VENUS M2 - BUILD EXPERIMENTAL CHUNKS')
    print('=' * 72)
    print(f'Documents          : {len(records)}')
    print(f'Chunk size         : {CHUNK_SIZE}')
    print(f'Overlap            : {OVERLAP}')
    print('Counter            : whitespace')
    print(f'Documents traites  : {len(records)}')
    print(f'Chunks generes     : {len(chunks)}')
    print('Documents en erreur: 0')
    print(f'Manifest           : {CHUNKS_MANIFEST_PATH}')
    print(f'Chunks             : {CHUNKS_PATH}')
    print()
    print('Construction terminee.')


if __name__ == '__main__':
    main()
