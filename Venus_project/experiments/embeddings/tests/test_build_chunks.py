import copy
import json
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_DIR))

from build_chunks import build_chunks


def record(content=' '.join(f'token-{index}' for index in range(12)), **overrides):
    value = {
        'id': 'ESTM_001',
        'title': 'Formation initiale',
        'category': 'formations',
        'url': 'https://www.estm.sn/formations',
        'captured_at': '2026-09-18T04:19:22.053784+00:00',
        'content': content,
    }
    value.update(overrides)
    return value


class BuildChunksTests(unittest.TestCase):
    def test_build_is_deterministic(self):
        records = [record()]
        self.assertEqual(build_chunks(copy.deepcopy(records)), build_chunks(copy.deepcopy(records)))

    def test_ids_restart_per_document_and_are_unique(self):
        chunks = build_chunks(
            [
                record(id='ESTM_001'),
                record(id='ESTM_002'),
            ],
            chunk_size=4,
            overlap=1,
        )
        ids = [chunk['chunk_id'] for chunk in chunks]
        self.assertEqual(ids, ['ESTM_001_C001', 'ESTM_001_C002', 'ESTM_001_C003', 'ESTM_001_C004',
                               'ESTM_002_C001', 'ESTM_002_C002', 'ESTM_002_C003', 'ESTM_002_C004'])
        self.assertEqual(len(ids), len(set(ids)))

    def test_metadata_and_source_are_preserved(self):
        chunk = build_chunks([record()])[0]
        self.assertEqual(chunk['source_id'], 'ESTM_001')
        self.assertEqual(chunk['title'], 'Formation initiale')
        self.assertEqual(chunk['category'], 'formations')
        self.assertEqual(chunk['url'], 'https://www.estm.sn/formations')
        self.assertEqual(chunk['capture_date'], '2026-09-18T04:19:22.053784+00:00')
        self.assertTrue(chunk['content'])

    def test_small_document_produces_one_chunk(self):
        chunks = build_chunks([record(content='un petit document')])
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['unit_count'], 3)

    def test_overlap_is_preserved(self):
        chunks = build_chunks([record()], chunk_size=4, overlap=1)
        first_tokens = chunks[0]['content'].split()
        second_tokens = chunks[1]['content'].split()
        self.assertEqual(first_tokens[-1], second_tokens[0])

    def test_invalid_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            build_chunks([record()], chunk_size=0)
        with self.assertRaises(ValueError):
            build_chunks([record()], overlap=-1)
        with self.assertRaises(ValueError):
            build_chunks([record()], chunk_size=4, overlap=4)

    def test_missing_source_or_content_is_rejected(self):
        with self.assertRaises(ValueError):
            build_chunks([record(id='')])
        with self.assertRaises(ValueError):
            build_chunks([record(content='   ')])

    def test_output_records_are_json_serializable(self):
        chunks = build_chunks([record()])
        json.dumps(chunks, ensure_ascii=False)


if __name__ == '__main__':
    unittest.main()
