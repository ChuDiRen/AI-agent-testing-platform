"""时间格式化工具"""
from datetime import datetime
from typing import Optional

class TimeFormatter:
    """统一时间格式化工具类"""
    
    # 统一时间格式
    STANDARD_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @staticmethod
    def format_datetime(dt: Optional[datetime]) -> Optional[str]:
        """格式化datetime对象为标准字符串格式 YYYY-MM-DD HH:MM:SS"""
        if dt is None:
            return None
        return dt.strftime(TimeFormatter.STANDARD_FORMAT)
    
    @staticmethod
    def format_datetime_dict(data: dict, time_fields: list = None) -> dict:
        """格式化字典中的时间字段"""
        if time_fields is None:
            time_fields = ['create_time', 'modify_time', 'last_login_time']
        
        result = data.copy()
        for field in time_fields:
            if field in result and isinstance(result[field], datetime):
                result[field] = TimeFormatter.format_datetime(result[field])
        
        return result
    
    @staticmethod
    def now_str() -> str:
        """获取当前时间的标准格式字符串"""
        return datetime.now().strftime(TimeFormatter.STANDARD_FORMAT)

    @staticmethod
    def datetime_to_str(dt: Optional[datetime]) -> Optional[str]:
        """兼容旧代码：等价于 format_datetime"""
        return TimeFormatter.format_datetime(dt)
