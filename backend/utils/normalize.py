from typing import Iterable, List
import math


def min_max_scale(values: Iterable[float]) -> List[float]:
	vals = [float(v) for v in values]
	if not vals:
		return []
	mn = min(vals)
	mx = max(vals)
	if math.isclose(mx, mn):
		return [0.0 for _ in vals]
	return [(v - mn) / (mx - mn) for v in vals]


def z_score(values: Iterable[float]) -> List[float]:
	vals = [float(v) for v in values]
	if not vals:
		return []
	mean = sum(vals) / len(vals)
	var = sum((v - mean) ** 2 for v in vals) / len(vals)
	std = math.sqrt(var)
	if math.isclose(std, 0.0):
		return [0.0 for _ in vals]
	return [(v - mean) / std for v in vals]

