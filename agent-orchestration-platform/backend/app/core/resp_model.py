"""
统一响应模型
"""
from typing import Generic, TypeVar, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RespModel(BaseModel):
    """统一响应模型"""

    code: int = Field(default=200, description="状态码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    total: Optional[int] = Field(default=None, description="总数（分页时使用）")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": {},
                "total": 100,
                "timestamp": "2024-01-01T00:00:00"
            }
        }

    @classmethod
    def ok_resp(cls, data: Any = None, msg: str = "success") -> "RespModel":
        """成功响应"""
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def ok_resp_list(cls, data: Any = None, total: int = 0, msg: str = "success") -> "RespModel":
        """成功响应（带分页）"""
        return cls(code=200, msg=msg, data=data, total=total)

    @classmethod
    def error_resp(cls, code: int = 500, msg: str = "error", data: Any = None) -> "RespModel":
        """错误响应"""
        return cls(code=code, msg=msg, data=data)


# 导出响应模型
__all__ = ["RespModel"]
