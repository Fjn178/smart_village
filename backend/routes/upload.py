from flask import Blueprint, request, jsonify
from database.db import db, tasks_db, IndicatorDefinition
from services.upload_service import process_upload_task
import threading
import uuid

upload_bp = Blueprint('upload', __name__, url_prefix='/api/data')

@upload_bp.route('/upload', methods=['POST'])
def upload_excel():
    # 1. 校验文件
    if 'file' not in request.files:
        return jsonify({"code": 400, "msg": "未上传文件"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "msg": "文件名为空"}), 400
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"code": 400, "msg": "仅支持 .xlsx 或 .xls 格式"}), 400

    # 2. 获取导入模式（前端传参 mode=append/overwrite）
    import_mode = request.form.get('mode', 'append')
    if import_mode not in ['append', 'overwrite']:
        return jsonify({"code": 400, "msg": "mode参数仅支持 append 或 overwrite"}), 400

    # 3. 预加载指标定义（映射到字典）
    indicators = IndicatorDefinition.query.all()
    indicator_map = {ind.indicator_name: ind for ind in indicators}
    if not indicator_map:
        return jsonify({"code": 500, "msg": "数据库未配置指标定义，请先初始化"}), 500

    # 4. 创建任务
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "status": "pending",
        "total": 0,
        "current": 0,
        "error": "",
        "detail_errors": []
    }

    # 5. 读取文件字节并启动后台线程
    file_bytes = file.read()
    thread = threading.Thread(
        target=process_upload_task,
        args=(task_id, file_bytes, import_mode, indicator_map)
    )
    thread.daemon = True
    thread.start()

    return jsonify({"code": 200, "taskId": task_id, "msg": "导入任务已开始"})

@upload_bp.route('/task/<taskId>', methods=['GET'])
def get_task_progress(taskId):
    task = tasks_db.get(taskId)
    if not task:
        return jsonify({"code": 404, "msg": "任务不存在"}), 404
    
    # 前端只需要这些字段
    return jsonify({
        "code": 200,
        "data": {
            "status": task["status"],
            "total": task["total"],
            "current": task["current"],
            "error": task.get("error", ""),
            "detail_errors": task.get("detail_errors", [])  # 逐行错误
        }
    })
