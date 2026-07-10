"""五维评分引擎。

该引擎用于对乡村发展或产业评估中的五个维度进行加权评分：
- industry：产业基础  
- resources：资源条件
- transport：交通条件
- policy：政策支持
- society：社会环境
"""

from __future__ import annotations

from typing import Any, Mapping, Optional


class FiveDimScoreEngine:
    """基于五个维度的加权评分器。"""

    DEFAULT_DIMENSIONS = ("industry", "resources", "transport", "policy", "society")
    DEFAULT_WEIGHTS = {
        "industry": 0.25,
        "resources": 0.20,
        "transport": 0.20,
        "policy": 0.20,
        "society": 0.15,
    }

    def __init__(self, weights: Optional[Mapping[str, float]] = None):
        self.weights = self._normalize_weights(weights or self.DEFAULT_WEIGHTS)

    def _normalize_weights(self, weights: Mapping[str, float]) -> dict[str, float]:
        normalized: dict[str, float] = {}
        total = sum(float(weights.get(dim, 0.0)) for dim in self.DEFAULT_DIMENSIONS)

        if total <= 0:
            default_weight = 1.0 / len(self.DEFAULT_DIMENSIONS)
            for dim in self.DEFAULT_DIMENSIONS:
                normalized[dim] = default_weight
            return normalized

        for dim in self.DEFAULT_DIMENSIONS:
            normalized[dim] = float(weights.get(dim, 0.0)) / total

        return normalized

    def _extract_score(self, value: Any) -> float:
        if value is None:
            return 0.0

        if isinstance(value, Mapping):
            for key in ("score", "value", "rating", "points"):
                if key in value and isinstance(value[key], (int, float)):
                    return self._normalize_score(float(value[key]))
            for nested_value in value.values():
                if isinstance(nested_value, (int, float)):
                    return self._normalize_score(float(nested_value))
            return 0.0

        if isinstance(value, (int, float)):
            return self._normalize_score(float(value))

        return 0.0

    def _normalize_score(self, score: float) -> float:
        if score <= 1:
            return round(score * 100.0, 2)
        return round(score, 2)

    def score(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """根据输入数据对五个维度进行加权评分。"""
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a mapping")

        dimension_scores: dict[str, dict[str, Any]] = {}
        total_score = 0.0

        dimensions_payload = payload.get("dimensions")
        if isinstance(dimensions_payload, Mapping):
            source_payload = dimensions_payload
        else:
            source_payload = payload

        for dim in self.DEFAULT_DIMENSIONS:
            raw_value = source_payload.get(dim)
            score = self._extract_score(raw_value)
            dimension_scores[dim] = {
                "score": score,
                "weight": round(self.weights[dim], 2),
            }
            total_score += score * self.weights[dim]

        return {
            "total_score": round(total_score, 2),
            "dimension_scores": dimension_scores,
            "dimension_count": len(self.DEFAULT_DIMENSIONS),
            "weights": {dim: round(weight, 4) for dim, weight in self.weights.items()},
        }

    def evaluate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """evaluate 是 score 的别名，便于在不同服务中复用。"""
        return self.score(payload)
