import os
import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import io
import logging

# ------------------- 配置 -------------------
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# 简单日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------- FastAPI 实例 -------------------
app = FastAPI(title="Excel 批量导入服务")

# ------------------- 任务状态存储（接口抽象，方便扩展） -------------------
class TaskStore:
    """任务状态存储基类，可替换为 Redis 实现"""
    def get(self, task_id: str):
        raise NotImplementedError
    def set(self, task_id: str, data: dict):
        raise NotImplementedError
    def update(self, task_id: str, **kwargs):
        raise NotImplementedError

class MemoryTaskStore(TaskStore):
    """基于内存的简单实现，仅适用于单进程开发环境"""
    def __init__(self):
        self._db = {}
    def get(self, task_id: str):
        return self._db.get(task_id)
    def set(self, task_id: str, data: dict):
        self._db[task_id] = data
    def update(self, task_id: str, **kwargs):
        if task_id in self._db:
            self._db[task_id].update(kwargs)

task_store = MemoryTaskStore()   # 生产环境替换为 RedisTaskStore

# ------------------- Pydantic 模型 -------------------
class TaskStatus(BaseModel):
    taskId: str
    status: str           # pending / processing / done / fail
    total: int = 0
    current: int = 0
    error: str = ""

class UploadResponse(BaseModel):
    code: int = 200
    message: str = "文件已接收，导入任务已启动"
    data: TaskStatus

# ------------------- 后台处理函数 -------------------
def process_excel_import(task_id: str, file_bytes: bytes):
    """后台解析 Excel 并逐行处理（替换为真实数据库操作）"""
    try:
        task_store.update(task_id, status="processing")

        # 1. 解析 Excel
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        if df.empty:
            raise ValueError("Excel 文件为空或无有效数据")

        # 清洗：NaN → None
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        total = len(records)
        task_store.update(task_id, total=total, current=0)

        # 2. 逐行处理（此处模拟，实际替换为数据库 insert）
        for idx, row in enumerate(records):
            # ---- 你的业务处理开始 ----
            # 示例：校验年龄字段
            age = row.get('年龄')
            if age is not None and not isinstance(age, (int, float)):
                raise ValueError(f"第 {idx+2} 行数据异常：年龄字段必须为数字")
            # 示例：插入数据库
            # db_session.add(YourModel(**row))
            # db_session.commit()
            # ---- 你的业务处理结束 ----

            task_store.update(task_id, current=idx + 1)

        # 全部成功
        task_store.update(task_id, status="done")

    except Exception as e:
        logger.error(f"任务 {task_id} 失败: {str(e)}")
        # 错误信息脱敏，避免暴露内部细节
        safe_error = "服务器处理异常，请检查文件格式或联系管理员"
        if isinstance(e, ValueError):
            safe_error = str(e)
        task_store.update(task_id, status="fail", error=safe_error)

# ------------------- 接口 1: 上传 Excel -------------------
@app.post("/api/data/upload", response_model=UploadResponse)
async def upload_excel(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    # ---- 文件校验 ----
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型，仅接受 {', '.join(ALLOWED_EXTENSIONS)} 格式")

    if file.content_type not in [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    ]:
        raise HTTPException(status_code=400, detail="文件类型校验失败，请上传有效的 Excel 文件")

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"文件大小超过 {MAX_FILE_SIZE / (1024*1024):.0f} MB 限制")
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")

    # ---- 创建任务 ----
    task_id = str(uuid.uuid4())
    task_store.set(task_id, {
        "status": "pending",
        "total": 0,
        "current": 0,
        "error": ""
    })

    background_tasks.add_task(process_excel_import, task_id, file_content)

    return UploadResponse(
        data=TaskStatus(
            taskId=task_id,
            status="pending",
            total=0,
            current=0,
            error=""
        )
    )

# ------------------- 接口 2: 查询进度 -------------------
@app.get("/api/data/task/{task_id}", response_model=TaskStatus)
async def get_task_progress(task_id: str):
    task = task_store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskStatus(
        taskId=task_id,
        status=task.get("status", "pending"),
        total=task.get("total", 0),
        current=task.get("current", 0),
        error=task.get("error", "")
    )

# ------------------- 接口 3: 取消任务（可选） -------------------
@app.post("/api/data/task/{task_id}/cancel")
async def cancel_task(task_id: str):
    task = task_store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task["status"] in ("done", "fail"):
        raise HTTPException(status_code=400, detail="任务已结束，无法取消")
    # 简单标记取消（后台处理函数需周期性检查此标志，实际实现需改造循环）
    task_store.update(task_id, status="cancelled", error="用户手动取消")
    return {"message": "取消请求已提交"}

# 启动命令：uvicorn main:app --reload
