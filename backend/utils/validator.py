from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple


class ValidationError(Exception):
	"""用于表示验证失败的异常，包含错误详情。"""

	def __init__(self, errors: List[Dict[str, Any]]):
		super().__init__("validation error")
		self.errors = errors


def validate_required(record: Dict[str, Any], required_fields: Iterable[str]) -> List[str]:
	missing = [f for f in required_fields if record.get(f) in (None, "", [])]
	return missing


def validate_type(value: Any, expected: str) -> bool:
	if value is None:
		return False
	expected = expected.lower()
	try:
		if expected in ("int", "integer"):
			int(value)
			return True
		if expected in ("float", "number"):
			float(value)
			return True
		if expected in ("str", "string"):
			return isinstance(value, str)
		if expected in ("bool", "boolean"):
			return isinstance(value, bool)
		if expected in ("list", "array"):
			return isinstance(value, (list, tuple))
	except Exception:
		return False
	# fallback: accept
	return True


def validate_range(value: Any, min_value: Optional[float], max_value: Optional[float]) -> bool:
	try:
		v = float(value)
	except Exception:
		return False
	if min_value is not None and v < min_value:
		return False
	if max_value is not None and v > max_value:
		return False
	return True


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(value: Any) -> bool:
	if not isinstance(value, str):
		return False
	return bool(_EMAIL_RE.match(value))


def validate_row_against_schema(row: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
	"""以 schema 校验一行数据。

	schema 格式示例：
	{
	  "name": {"required": True, "type": "str"},
	  "age": {"required": False, "type": "int", "min": 0, "max": 120},
	  "email": {"required": False, "type": "str", "format": "email"}
	}
	返回错误列表，空表示通过。
	"""
	errors: List[Dict[str, Any]] = []
	for field, rules in schema.items():
		val = row.get(field)
		if rules.get("required") and (val is None or val == ""):
			errors.append({"field": field, "code": "required", "message": "missing required field"})
			continue

		t = rules.get("type")
		if t and val not in (None, ""):
			if not validate_type(val, t):
				errors.append({"field": field, "code": "type", "message": f"invalid type, expected {t}"})
				continue

		# range checks
		if val not in (None, "") and ("min" in rules or "max" in rules):
			minv = rules.get("min")
			maxv = rules.get("max")
			if not validate_range(val, minv, maxv):
				errors.append({"field": field, "code": "range", "message": f"value out of range [{minv}, {maxv}]"})

		fmt = rules.get("format")
		if fmt and val not in (None, ""):
			if fmt == "email" and not validate_email(val):
				errors.append({"field": field, "code": "format", "message": "invalid email format"})

	return errors

