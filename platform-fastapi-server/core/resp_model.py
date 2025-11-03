"""响应模型"""
from typing import Any, Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel
from .time_utils import TimeFormatter
from .logger import Logger

class respModel:
    
    @staticmethod
    def ok_resp(obj=None, msg=None, dic_t=None) -> Dict: # 单条数据响应
        rsp = {"code": 200, "msg": msg, "data": {}, "trace_id": Logger.get_trace_id()}
        if obj:
            if isinstance(obj, BaseModel):
                rsp["data"].update(obj.model_dump())
            elif isinstance(obj, dict):
                rsp["data"].update(obj)
            else:
                rsp["data"].update(respModel._model_to_dict(obj))
        if dic_t:
            rsp["data"].update(dic_t)
        return rsp
    
    @staticmethod
    def ok_resp_list(obj=None, msg=None, lst=None, total=0) -> Dict: # 列表数据响应
        rsp = {"code": 200, "msg": msg, "total": total, "data": [], "trace_id": Logger.get_trace_id()}
        if lst:
            for item in lst:
                if isinstance(item, BaseModel):
                    rsp["data"].append(item.model_dump())
                elif isinstance(item, dict):
                    rsp["data"].append(item)
                else:
                    rsp["data"].append(respModel._model_to_dict(item))
        return rsp
    
    @staticmethod
    def ok_resp_listdata(obj=None, msg=None, lst=None, total=0) -> Dict: # 自定义列表响应
        return {"code": 200, "msg": msg, "total": total, "data": lst if lst else [], "trace_id": Logger.get_trace_id()}
    
    @staticmethod
    def ok_resp_simple(lst=None, msg=None) -> Dict: # 简单数据响应
        return {"code": 200, "msg": msg, "data": lst, "trace_id": Logger.get_trace_id()}
    
    @staticmethod
    def ok_resp_simple_list(lst=None, msg=None, total=0) -> Dict: # 简单列表响应
        return {"code": 200, "msg": msg, "data": lst, "total": total, "trace_id": Logger.get_trace_id()}
    
    @staticmethod
    def ok_resp_text(msg=None, data=None) -> Dict: # 文本响应
        return {"code": 200, "msg": msg, "data": data, "trace_id": Logger.get_trace_id()}
    
    @staticmethod
    def ok_resp_tree(treeData, msg) -> Dict: # 树形数据响应
        return {"code": 200, "msg": msg, "data": treeData, "trace_id": Logger.get_trace_id()}
    
    @staticmethod
    def error_resp(msg) -> Dict: # 错误响应
        return {"code": -1, "msg": msg, "trace_id": Logger.get_trace_id()}
    
    @staticmethod
    def _model_to_dict(obj) -> Dict: # SQLModel对象转字典
        result = {}
        if hasattr(obj, '__dict__'):
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if isinstance(value, datetime):
                        result[key] = TimeFormatter.format_datetime(value)
                    else:
                        result[key] = value
        return result
