import threading
import uuid
import time
from database.db import db, Village, VillageIndicator, tasks_db
from utils.excel_parser import parse_and_validate_excel

def process_upload_task(task_id, file_bytes, import_mode, indicator_map):
    """
    后台线程执行的实际导入逻辑
    """
    try:
        tasks_db[task_id]['status'] = 'processing'
        tasks_db[task_id]['total'] = 0
        tasks_db[task_id]['current'] = 0

        # 1. 解析校验
        is_success, valid_rows, errors = parse_and_validate_excel(file_bytes, indicator_map)
        
        if not is_success:
            tasks_db[task_id]['status'] = 'fail'
            tasks_db[task_id]['error'] = "; ".join([e['msg'] for e in errors if 'msg' in e]) or "数据校验失败"
            tasks_db[task_id]['detail_errors'] = errors
            return

        total_rows = len(valid_rows)
        tasks_db[task_id]['total'] = total_rows

        # 2. 逐条处理入库
        for idx, row_data in enumerate(valid_rows):
            # 检查村庄是否已存在（按名称+乡镇粗略去重，实际可按唯一ID）
            existing_village = Village.query.filter_by(
                village_name=row_data['village_name'],
                town=row_data['town']
            ).first()

            if existing_village:
                if import_mode == 'append':
                    # 追加模式：跳过已存在
                    tasks_db[task_id]['current'] = idx + 1
                    continue
                elif import_mode == 'overwrite':
                    # 覆盖模式：先删旧指标，再用新数据
                    village_id = existing_village.village_id
                    VillageIndicator.query.filter_by(village_id=village_id).delete()
            else:
                # 新增村庄
                village_id = f"V{int(time.time())}{uuid.uuid4().hex[:6]}"
                new_village = Village(
                    village_id=village_id,
                    village_name=row_data['village_name'],
                    town=row_data['town']
                )
                db.session.add(new_village)
                db.session.flush()  # 获取ID
                existing_village = new_village

            # 插入指标值
            for ind_id, val_dict in row_data['indicators'].items():
                indicator_record = VillageIndicator(
                    village_id=existing_village.village_id,
                    indicator_id=ind_id,
                    indicator_value=val_dict.get('numeric'),
                    text_value=val_dict.get('text', '')
                )
                db.session.add(indicator_record)

            # 每处理一条提交一次（小数据量可接受）
            db.session.commit()
            tasks_db[task_id]['current'] = idx + 1

        # 完成
        tasks_db[task_id]['status'] = 'done'
        
    except Exception as e:
        db.session.rollback()
        tasks_db[task_id]['status'] = 'fail'
        tasks_db[task_id]['error'] = str(e)