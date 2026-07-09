import pandas as pd
import io
from typing import List, Dict, Any, Optional, Union

def parse_excel(
    file_bytes: bytes,
    sheet_name: Union[str, int] = 0,
    dtype: Optional[Dict[str, type]] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    将上传的Excel字节流解析为字典列表，并做基础清洗。

    :param file_bytes: Excel文件的二进制数据
    :param sheet_name: 工作表名称或索引，默认第一个工作表
    :param dtype: 指定列的数据类型，如 {'手机号': str} 避免精度丢失
    :param kwargs: 其他传递给 pd.read_excel 的参数（如 skiprows, usecols）
    :return: 列表，每个元素为一行数据的字典
    """
    try:
        df = pd.read_excel(
            io.BytesIO(file_bytes),
            sheet_name=sheet_name,
            engine='openpyxl',
            dtype=dtype,
            **kwargs
        )
        # 删除全为空的行
        df = df.dropna(how='all')
        # 将NaN替换为None，以便JSON序列化
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
    except pd.errors.EmptyDataError:
        raise ValueError("Excel 文件为空或未包含有效数据")
    except Exception as e:
        raise ValueError(f"Excel 解析失败: {str(e)}") from e
