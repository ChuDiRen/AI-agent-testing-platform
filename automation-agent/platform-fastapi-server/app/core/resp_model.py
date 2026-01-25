"""
统一响应模型模块
"""
from typing import Optional, Any, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class ResponseModel(BaseModel):
    """统一响应模型"""
    code: int = 200
    msg: str = "success"
    data: Optional[Any] = None
    total: Optional[int] = None
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    
    class Config:
        arbitrary_types_allowed = True


def serialize_value(value: Any) -> Any:
    """序列化值，处理日期时间和对象"""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items() if not k.startswith('_')}
    elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool)):
        return serialize_object(value)
    return value


def serialize_object(obj: Any) -> dict:
    """序列化对象为字典"""
    from sqlalchemy.inspection import inspect as sqlalchemy_inspect
    from sqlalchemy.exc import NoInspectionAvailable
    
    if isinstance(obj, dict):
        return {k: serialize_value(v) for k, v in obj.items() if not k.startswith('_')}
    
    result = {}
    
    # 处理SQLAlchemy模型
    try:
        mapper = sqlalchemy_inspect(obj)
        # 获取所有列属性
        for column in mapper.mapper.column_attrs:
            key = column.key
            value = getattr(obj, key, None)
            result[key] = serialize_value(value)
        
        # 获取动态属性（如children）
        for attr in dir(obj):
            if not attr.startswith('_') and attr not in result:
                try:
                    value = getattr(obj, attr)
                    if not callable(value) and not hasattr(mapper.mapper, attr):
                        result[attr] = serialize_value(value)
                except:
                    pass
        
        return result
    except (NoInspectionAvailable, AttributeError):
        pass
    
    # 处理普通对象
    if hasattr(obj, '__dict__'):
        for key, value in vars(obj).items():
            if not key.startswith('_'):
                # 直接处理值
                if isinstance(value, datetime):
                    result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    result[key] = value.strftime('%Y-%m-%d')
                elif isinstance(value, list):
                    result[key] = [serialize_object(item) if hasattr(item, '__dict__') else item for item in value]
                elif hasattr(value, '__dict__') and type(value).__name__ not in ['str', 'int', 'float', 'bool', 'NoneType']:
                    result[key] = serialize_object(value)
                else:
                    result[key] = value
    
    return result


class RespModel:
    """响应工具类"""
    
    @staticmethod
    def success(data: Any = None, msg: str = "success", total: Optional[int] = None) -> ResponseModel:
        """
        成功响应
        
        Args:
            data: 数据（对象、列表或字典）
            msg: 响应消息
            total: 总数（用于分页）
        
        Returns:
            ResponseModel
        """
        if data is not None:
            if isinstance(data, list):
                data = [serialize_object(item) for item in data]
            elif not isinstance(data, (dict, str, int, float, bool)):
                data = serialize_object(data)
        
        return ResponseModel(code=200, msg=msg, data=data, total=total)
    
    @staticmethod
    def error(msg: str, code: int = -1) -> ResponseModel:
        """
        错误响应
        
        Args:
            msg: 错误消息
            code: 错误码
        
        Returns:
            ResponseModel
        """
        return ResponseModel(code=code, msg=msg, data=None)
