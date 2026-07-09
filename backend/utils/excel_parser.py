import pandas as pd
import io

def parse_excel(file_bytes: bytes):
    """
    将上传的Excel字节流解析为字典列表，并做基础清洗
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        
        # 清洗：删除全为空的行
        df = df.dropna(how='all')
        # 清洗：将NaN（空值）替换为None，便于JSON序列化
        df = df.where(pd.notnull(df), None)
        
        # 转为列表字典，例如：[{"姓名": "张三", "年龄": 25}, ...]
        return df.to_dict(orient='records')
    except Exception as e:
        raise ValueError(f"Excel解析失败: {str(e)}")