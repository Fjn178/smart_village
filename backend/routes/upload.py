# routes/upload.py
import io
import pandas as pd
from flask import send_file
from database.db import IndicatorDefinition

@upload_bp.route('/template', methods=['GET'])
def download_template():
    """
    生成完全匹配《智联乡策》标准的多 Sheet Excel 模板
    """
    # 1. 查询所有指标，按一级分类（category_l1）分组
    indicators = IndicatorDefinition.query.order_by(
        IndicatorDefinition.category_l1,
        IndicatorDefinition.indicator_id
    ).all()
    
    # 分类字典
    groups = {}
    for ind in indicators:
        cat = ind.category_l1 or '其他指标'
        groups.setdefault(cat, []).append(ind)

    # 2. 写入内存 Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # ---------- Sheet 1: 村庄基本信息 ----------
        basic_fields = [
            '村庄名称', '所属省份', '所属地市', '所属区县', '所属乡镇',
            '总人口', '户数'
        ]
        df_basic = pd.DataFrame({
            '字段': basic_fields,
            '填写内容': [''] * len(basic_fields)  # 留空供用户填写
        })
        df_basic.to_excel(writer, sheet_name='村庄基本信息', index=False)

        # ---------- 后续 Sheet: 按分类生成指标表 ----------
        for cat_name, ind_list in groups.items():
            # Excel Sheet 名称不能超过 31 个字符，截断处理
            sheet_name = cat_name[:31]
            rows = []
            for ind in ind_list:
                rows.append([
                    ind.indicator_id,
                    ind.indicator_name,
                    ind.category_l1 or '',
                    ind.category_l2 or '',
                    ind.indicator_desc or '',  # 对应模板里的“指标说明”
                    ind.unit or '',
                    ind.data_type or '数值',
                    ''  # 最后一列：指标值（用户填写）
                ])
            # 定义列名（完全照搬你模板里的表头，再加一列“指标值”）
            columns = ['indicator_id', '指标名称', '一级分类', '二级分类', '指标说明', '单位', '数据类型', '指标值']
            df = pd.DataFrame(rows, columns=columns)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='智联乡策_村庄数据填报模板.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
