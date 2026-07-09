"""简单的算法流水线入口。"""

from __future__ import annotations

from typing import Any, Mapping

from .score_engine import FiveDimScoreEngine


class AlgorithmPipeline:
    """将评分引擎串联到当前的算法流程中。"""

    def __init__(self, score_engine: FiveDimScoreEngine | None = None):
        self.score_engine = score_engine or FiveDimScoreEngine()

    def run(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.score_engine.score(payload)
