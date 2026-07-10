from flask import jsonify


def success(data=None, message="ok", code=0):
	"""统一成功返回格式。"""
	payload = {"code": code, "message": message, "data": data}
	return jsonify(payload)


def error(message="error", code=1, data=None):
	"""统一错误返回格式。"""
	payload = {"code": code, "message": message, "data": data}
	return jsonify(payload)
 