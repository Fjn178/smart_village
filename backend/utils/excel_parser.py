import pandas as pd
import io
import re
from database.db import IndicatorDefinition

def parse_and_validate_excel(file_bytes, indicator_map):
    """
    :param file_bytes: 上传的文件字节流
    :param indicator_map: 从数据库查出的 {指标名称: 指标对象} 字典
    :return: (is_success, data_rows, errors_detail)
    """
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    except Exception as e:
        return False, [], [{"type": "global", "msg": f"Excel解析失败: {str(e)}"}]

    # 清洗空行
    df = df.dropna(how='all')
    if df.empty:
        return False, [], [{"type": "global", "msg": "Excel为空，请填入数据"}]

    # 1. 校验表头是否匹配指标库
    required_columns = {'村庄名称', '所属乡镇'}  # 必填基础字段
    headers = df.columns.tolist()
    # 检查必填基础列
    if not required_columns.issubset(set(headers)):
        return False, [], [{"type": "global", "msg": f"Excel缺少必填列：{required_columns - set(headers)}"}]

    # 构建列名 -> indicator_id 映射
    col_to_indicator = {}
    matched_indicators = set()
    for col in headers:
        if col in indicator_map:
            col_to_indicator[col] = indicator_map[col].indicator_id
            matched_indicators.add(col)

    errors = []
    valid_rows = []  # 最终返回 [{village_name, town, indicators:{id:value}}]

    # 2. 逐行遍历（从第0行开始）
    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel行号（从1开始，加上表头占1行）
        row_errors = []
        village_name = str(row.get('村庄名称', '')).strip()
        town = str(row.get('所属乡镇', '')).strip()

        if not village_name or village_name == 'nan':
            row_errors.append(f"第{row_num}行：村庄名称为空")
        if not town or town == 'nan':
            row_errors.append(f"第{row_num}行：所属乡镇为空")

        # 存储该行的指标值
        indicator_values = {}
        for col, ind_id in col_to_indicator.items():
            val = row.get(col)
            indicator_def = indicator_map[col]
            
            # 文本类型直接存字符串
            if indicator_def.data_type == '文本':
                indicator_values[ind_id] = {'text': str(val) if pd.notna(val) else ''}
                continue
            
            # 数值类型：校验是否合法数字及范围
            if pd.isna(val):
                row_errors.append(f"第{row_num}行：{col} 数值缺失")
                continue
            try:
                num_val = float(val)
                # 根据计划书，很多指标是百分比或特定范围，这里做通用范围校验（0-10000）
                if num_val < 0:
                    row_errors.append(f"第{row_num}行：{col} 不能为负数")
                indicator_values[ind_id] = {'numeric': num_val}
            except (ValueError, TypeError):
                row_errors.append(f"第{row_num}行：{col} 格式错误（应为数字）")

        # 如果该行有错误，累计错误
        if row_errors:
            errors.append({"row": row_num, "errors": row_errors})
        else:
            # 组装有效数据
            valid_rows.append({
                "village_name": village_name,
                "town": town,
                "indicators": indicator_values
            })

    # 判断整体是否成功（没有错误即为成功）
    if errors:
        return False, valid_rows, errors  # 有错误时，valid_rows仅包含正确行，但整体失败
    return True, valid_rows, []
