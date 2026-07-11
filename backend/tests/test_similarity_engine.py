import os
import sys
import sqlite3
import tempfile
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.algorithms import similarity_engine as engine


class TestSimilarityEngine(unittest.TestCase):
    def test_indicator_ids_length(self):
        self.assertEqual(len(engine.INDICATOR_IDS), 156)
        self.assertEqual(engine.INDICATOR_IDS[0], 1)
        self.assertEqual(engine.INDICATOR_IDS[-1], 156)

    def test_weighted_euclidean_distance_properties(self):
        target = [1.0, 2.0, 3.0]
        case = [1.0, 2.0, 3.0]
        weights = [1.0, 1.0, 1.0]

        self.assertEqual(engine.weighted_euclidean_distance(target, case, weights), 0.0)

        case2 = [2.0, 1.0, 4.0]
        d1 = engine.weighted_euclidean_distance(target, case2, weights)
        d2 = engine.weighted_euclidean_distance(case2, target, weights)
        self.assertAlmostEqual(d1, d2, places=6)

        with self.assertRaises(ValueError):
            engine.weighted_euclidean_distance(target, case2, [1.0, 1.0])

    def test_distance_to_similarity_score_exponential(self):
        self.assertAlmostEqual(engine.distance_to_similarity_score(0.0), 100.0, places=6)
        self.assertAlmostEqual(engine.distance_to_similarity_score(1.0), 100.0 * math.exp(-0.3), places=4)
        self.assertAlmostEqual(engine.distance_to_similarity_score(2.0), 100.0 * math.exp(-0.6), places=4)
        self.assertGreater(engine.distance_to_similarity_score(0.0), engine.distance_to_similarity_score(1.0))

    def test_normalize_vector_zscore(self):
        vector = [1.0, 2.0, 3.0, 4.0, 5.0]
        normalized = engine._normalize_vector(vector)
        self.assertEqual(len(normalized), len(vector))
        self.assertAlmostEqual(sum(normalized), 0.0, places=6)
        self.assertAlmostEqual(
            (sum((x - sum(normalized) / len(normalized)) ** 2 for x in normalized) / len(normalized)) ** 0.5,
            1.0,
            places=5,
        )

    def test_find_indicator_category_boundaries(self):
        self.assertEqual(engine._find_indicator_category(1), "population")
        self.assertEqual(engine._find_indicator_category(18), "land")
        self.assertEqual(engine._find_indicator_category(31), "nature")
        self.assertEqual(engine._find_indicator_category(44), "transport")
        self.assertEqual(engine._find_indicator_category(67), "industry")
        self.assertEqual(engine._find_indicator_category(97), "economy")
        self.assertEqual(engine._find_indicator_category(113), "policy")
        self.assertEqual(engine._find_indicator_category(136), "culture")
        self.assertEqual(engine._find_indicator_category(156), "culture")

    def test_get_category_median(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute(
            "CREATE TABLE village_indicators (village_id INTEGER, indicator_id INTEGER, value REAL)"
        )
        conn.executemany(
            "INSERT INTO village_indicators (village_id, indicator_id, value) VALUES (?, ?, ?)",
            [
                (1, 1, 10.0),
                (1, 2, 20.0),
                (1, 3, 30.0),
            ],
        )
        conn.commit()

        median = engine._get_category_median(conn, 1)
        self.assertEqual(median, 20.0)

        conn.close()

    def test_get_case_count_without_database(self):
        count = engine.get_case_count()
        self.assertGreaterEqual(count, 0)

    def test_match_similar_cases_integration(self):
        original_db_path = os.environ.get("DATABASE_PATH")
        fd, temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            os.environ["DATABASE_PATH"] = temp_path
            conn = sqlite3.connect(temp_path)
            conn.row_factory = sqlite3.Row
            conn.execute(
                "CREATE TABLE village_indicators (village_id INTEGER, indicator_id INTEGER, value REAL)"
            )
            conn.execute(
                "CREATE TABLE case_library (id INTEGER PRIMARY KEY AUTOINCREMENT, village_id INTEGER, case_name TEXT, industry TEXT, result TEXT, key_practices TEXT, special_notes TEXT)"
            )
            values = [
                (1, 1, 10.0),
                (1, 18, 20.0),
                (2, 1, 12.0),
                (2, 18, 18.0),
            ]
            conn.executemany(
                "INSERT INTO village_indicators (village_id, indicator_id, value) VALUES (?, ?, ?)",
                values,
            )
            conn.execute(
                "INSERT INTO case_library (village_id, case_name, industry, result, key_practices, special_notes) VALUES (?, ?, ?, ?, ?, ?)",
                (2, "测试案例", "测试产业", "测试结果", "关键做法", "备注"),
            )
            conn.commit()
            conn.close()

            results = engine.match_similar_cases(1, top_n=1, weight_type="equal", use_mock=False)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["case_name"], "测试案例")
            self.assertGreaterEqual(results[0]["similarity_score"], 0)
            self.assertLessEqual(results[0]["similarity_score"], 100)
        finally:
            if original_db_path is not None:
                os.environ["DATABASE_PATH"] = original_db_path
            else:
                os.environ.pop("DATABASE_PATH", None)
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
