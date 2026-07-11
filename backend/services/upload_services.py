# services/upload_service.py
import threading
import uuid
import time
from database.db import db, Village, VillageIndicator, tasks_db
from utils.excel_parser import parse_and_validate_excel

def process_upload_task(task_id, file_bytes, import_mode, indicator_map_by_id):
    try:
        tasks_db[task_id]['status'] = 'processing'
        tasks_db[task_id]['total'] = 1  # 只有 1 个村庄
        tasks_db[task_id]['current'] = 0

        # 1. 解析 Excel
        is_success, basic_info, indicators_values, errors = parse_and_validate_excel(
            file_bytes, indicator_map_by_id
        )

        if not is_success:
            tasks_db[task_id]['status'] = 'fail'
            tasks_db[task_id]['error'] = '数据校验失败'
            tasks_db[task_id]['detail_errors'] = errors
            return

        village_name = basic_info['village_name']
        town = basic_info['town']

        # 2. 查找村庄是否已存在（按名称+乡镇）
        existing_village = Village.query.filter_by(
            village_name=village_name,
            town=town
        ).first()

        if existing_village:
            if import_mode == 'append':
                # 追加模式：已存在则跳过
                tasks_db[task_id]['status'] = 'done'
                tasks_db[task_id]['current'] = 1
                tasks_db[task_id]['error'] = f'村庄 "{village_name}" 已存在，追加模式已跳过'
                return
            elif import_mode == 'overwrite':
                # 覆盖模式：删除旧指标
                village_id = existing_village.village_id
                VillageIndicator.query.filter_by(village_id=village_id).delete()
                village_obj = existing_village
        else:
            # 新增村庄
            village_id = f"V{int(time.time())}{uuid.uuid4().hex[:6]}"
            village_obj = Village(
                village_id=village_id,
                village_name=village_name,
                province=basic_info.get('province', ''),
                city=basic_info.get('city', ''),
                county=basic_info.get('county', ''),
                town=town
            )
            db.session.add(village_obj)
            db.session.flush()

        # 3. 插入/更新指标值（包括总人口、户数）
        # 先把基本信息里的总人口、户数转成指标
        if basic_info.get('total_population'):
            indicators_values[1] = float(basic_info['total_population'])  # ID 1 是户籍人口
        if basic_info.get('households'):
            indicators_values[3] = float(basic_info['households'])        # ID 3 是户数

        for ind_id, value in indicators_values.items():
            # 只保存非空值
            if value is None or value == '':
                continue
            indicator_def = indicator_map_by_id.get(ind_id)
            if not indicator_def:
                continue
            
            record = VillageIndicator(
                village_id=village_obj.village_id,
                indicator_id=ind_id,
                indicator_value=value if indicator_def.data_type == '数值' else None,
                text_value=value if indicator_def.data_type == '文本' else None
            )
            db.session.add(record)

        db.session.commit()
        tasks_db[task_id]['status'] = 'done'
        tasks_db[task_id]['current'] = 1

    except Exception as e:
        db.session.rollback()
        tasks_db[task_id]['status'] = 'fail'
        tasks_db[task_id]['error'] = str(e)