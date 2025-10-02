"""数据导出工具"""
import csv
import json
from io import StringIO
from typing import List, Dict, Any
from datetime import datetime


def export_to_csv(data: List[Dict[str, Any]], headers: List[str]) -> str:
    """导出为CSV格式
    
    Args:
        data: 数据列表
        headers: 表头列表
        
    Returns:
        str: CSV内容
    """
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    
    writer.writeheader()
    for row in data:
        # 只保留headers中的字段
        filtered_row = {k: v for k, v in row.items() if k in headers}
        writer.writerow(filtered_row)
    
    return output.getvalue()


def export_to_json(data: List[Dict[str, Any]]) -> str:
    """导出为JSON格式
    
    Args:
        data: 数据列表
        
    Returns:
        str: JSON内容
    """
    def json_serial(obj):
        """JSON序列化datetime对象"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    return json.dumps(data, ensure_ascii=False, indent=2, default=json_serial)


def export_to_excel(data: List[Dict[str, Any]], headers: List[str]) -> bytes:
    """导出为Excel格式（需要安装 openpyxl）
    
    Args:
        data: 数据列表
        headers: 表头列表
        
    Returns:
        bytes: Excel文件内容
    """
    try:
        from openpyxl import Workbook
        from io import BytesIO
        
        wb = Workbook()
        ws = wb.active
        
        # 写入表头
        ws.append(headers)
        
        # 写入数据
        for row in data:
            ws.append([row.get(h) for h in headers])
        
        # 保存到内存
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output.getvalue()
    except ImportError:
        raise ImportError("需要安装 openpyxl: pip install openpyxl")

