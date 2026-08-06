import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import embed_link


class ChunkedEmbeddingTests(unittest.TestCase):
    def test_clean_prose_removes_code_and_preserves_labels(self):
        text = (
            "Intro [useful link](https://example.com).\n"
            "```r\nsecret_code()\n```\n"
            "![Important chart caption](chart.png)\n"
            "<!-- RELATED:BEGIN -->ignore me<!-- RELATED:END -->"
        )

        cleaned = embed_link.clean_prose(text)

        self.assertIn("useful link", cleaned)
        self.assertIn("Important chart caption", cleaned)
        self.assertNotIn("secret_code", cleaned)
        self.assertNotIn("ignore me", cleaned)

    def test_chunking_covers_end_and_respects_limit(self):
        length = 10_000
        starts = embed_link.bounded_chunk_starts(
            length, size=100, overlap=10, max_chunks=7)

        self.assertEqual(len(starts), 7)
        self.assertEqual(starts[0], 0)
        self.assertEqual(starts[-1], length - 100)
        self.assertEqual(starts, sorted(set(starts)))

    def test_current_size_text_is_fully_chunked(self):
        text = "word " * 2_000
        token_count = len(embed_link._ENC.encode(text, disallowed_special=()))
        starts = embed_link.bounded_chunk_starts(
            token_count,
            embed_link.CHUNK_TOKENS,
            embed_link.CHUNK_OVERLAP,
            embed_link.MAX_CHUNKS,
        )

        self.assertEqual(starts[0], 0)
        self.assertEqual(starts[-1] + embed_link.CHUNK_TOKENS, token_count)

    def test_pair_score_is_symmetric_and_uses_multiple_passages(self):
        cross = np.array([[0.9, 0.2], [0.4, 0.8]], dtype=np.float32)

        forward = embed_link.pair_score(cross)
        reverse = embed_link.pair_score(cross.T)

        self.assertAlmostEqual(forward, reverse)
        self.assertAlmostEqual(forward, 0.85)


if __name__ == "__main__":
    unittest.main()
