"""
统一响应模型模块
从 Flask 迁移并适配 FastAPI
"""
from typing import Optional, Any, List
from datetime import date, datetime
from pydantic import BaseModel


class ResponseModel(BaseModel):
    """统一响应模型"""
    code: int = 200
    msg: Optional[str] = "success"
    data: Optional[Any] = None
    total: Optional[int] = None
    timestamp: int = int(datetime.now().timestamp() * 1000)


class RespModel(BaseModel):
    """响应工具类（继承BaseModel以支持FastAPI的response_model）"""

    @staticmethod
    def ok_resp(obj: Any = None, msg: str = "success", dic_t: dict = None) -> ResponseModel:
        """
        成功响应（单个对象）
        
        Args:
            obj: 数据对象（模型实例或字典）
            msg: 响应消息
            dic_t: 额外的字典数据
        
        Returns:
            ResponseModel 对象
        """
        data = {}
        if obj:
            data.update(RespModel._get_custom_attributes(obj))
        if dic_t:
            data.update(dic_t)
        return ResponseModel(code=200, msg=msg, data=data)
    
    @staticmethod
    def ok_resp_list(lst: List[Any], total: int = 0, msg: str = "success") -> ResponseModel:
        """
        列表响应
        
        Args:
            lst: 数据对象列表
            total: 总数
            msg: 响应消息
        
        Returns:
            ResponseModel 对象
        """
        lst_data = []
        for obj in lst:
            lst_data.append(RespModel._get_custom_attributes(obj))
        return ResponseModel(code=200, msg=msg, data=lst_data, total=total)
    
    @staticmethod
    def ok_resp_simple(data: Any = None, msg: str = "success") -> ResponseModel:
        """
        简单响应（直接返回数据）
        
        Args:
            data: 任意数据
            msg: 响应消息
        
        Returns:
            ResponseModel 对象
        """
        return ResponseModel(code=200, msg=msg, data=data)
    
    @staticmethod
    def ok_resp_simple_list(lst: List[Any], msg: str = "success", total: int = 0) -> ResponseModel:
        """
        简单列表响应（不转换对象属性）
        
        Args:
            lst: 列表数据
            msg: 响应消息
            total: 总数
        
        Returns:
            ResponseModel 对象
        """
        return ResponseModel(code=200, msg=msg, data=lst, total=total)
    
    @staticmethod
    def ok_resp_text(msg: str = "success", data: Any = None) -> ResponseModel:
        """
        文本响应
        
        Args:
            msg: 响应消息
            data: 数据
        
        Returns:
            ResponseModel 对象
        """
        return ResponseModel(code=200, msg=msg, data=data)
    
    @staticmethod
    def ok_resp_tree(treeData: Any, msg: str = "success") -> ResponseModel:
        """
        树形数据响应
        
        Args:
            treeData: 树形数据
            msg: 响应消息
        
        Returns:
            ResponseModel 对象
        """
        return ResponseModel(code=200, msg=msg, data=treeData)
    
    @staticmethod
    def ok_resp_file(file_path: str, content_type: str, file_name: str):
        """
        返回文件附件
        
        Args:
            file_path: 文件路径
            content_type: 内容类型
            file_name: 文件名
        
        Returns:
            FastAPI FileResponse 对象
        """
        from fastapi.responses import FileResponse
        try:
            return FileResponse(
                path=file_path,
                media_type=content_type,
                filename=file_name
            )
        except Exception as e:
            return RespModel.error_resp(f"文件处理失败: {str(e)}")
    
    @staticmethod
    def error_resp(msg: str, code: int = -1) -> ResponseModel:
        """
        错误响应
        
        Args:
            msg: 错误消息
            code: 错误码
        
        Returns:
            ResponseModel 对象
        """
        return ResponseModel(code=code, msg=msg)
    
    @staticmethod
    def _get_custom_attributes(obj: Any) -> dict:
        """
        获取对象的自定义属性
        
        Args:
            obj: 数据对象或字典
        
        Returns:
            属性字典
        """
        custom_attributes = {}
        # 处理字典和对象两种情况
        if isinstance(obj, dict):
            attributes = obj.items()  # 字典直接遍历键值对
        else:
            attributes = vars(obj).items()  # 其他对象使用 vars
        
        # 过滤掉内置属性和方法
        for attribute, value in attributes:
            if not attribute.startswith('__') and not callable(value) and not attribute.startswith('_'):
                # 时间格式转换, 如果是 datetime
                if isinstance(value, datetime) or isinstance(value, date):
                    value = datetime.strftime(value, '%Y-%m-%d %H:%M:%S')
                custom_attributes[attribute] = value
        return custom_attributes

# 别名
respModel = RespModel
