import unittest
from backend.algorithms.score_engine import FiveDimScoreEngine


class TestFiveDimScoreEngine(unittest.TestCase):
    def test_weighted_scoring_with_default_dimensions(self):
        engine = FiveDimScoreEngine()
        payload = {
            "industry": {"score": 90},
            "resources": {"score": 60},
            "transport": {"score": 70},
            "policy": {"score": 80},
            "society": {"score": 50},
        }

        result = engine.score(payload)

        self.assertEqual(result["total_score"], 72.0)
        self.assertEqual(result["dimension_scores"]["industry"]["score"], 90)
        self.assertEqual(result["dimension_scores"]["industry"]["weight"], 0.25)
        self.assertEqual(result["dimension_count"], 5)


if __name__ == "__main__":
    unittest.main()
