"""
系统设置 API 端点
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.resp_model import RespModel, ResponseModel
from app.core.deps import get_current_user_model
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/settings", tags=["系统设置"])


class BasicSettings(BaseModel):
    systemName: str
    systemDesc: str
    language: str
    timezone: str


class TestSettings(BaseModel):
    defaultTimeout: int
    maxRetries: int
    concurrency: int
    continueOnFailure: bool
    autoGenerateReport: bool


class NotificationSettings(BaseModel):
    emailEnabled: bool
    wechatEnabled: bool
    dingdingEnabled: bool
    feishuEnabled: bool
    notifyOn: list[str]


class SecuritySettings(BaseModel):
    sessionTimeout: int
    passwordStrength: str
    loginLockEnabled: bool
    maxLoginAttempts: int


@router.get("", response_model=ResponseModel)
async def get_settings():
    """获取系统设置"""
    try:
        print("Settings API called")
        # 返回默认的系统设置
        settings_data = {
            "basic": {
                "systemName": "大熊AI自动化测试",
                "systemDesc": "专业的接口测试管理解决方案",
                "language": "zh-CN",
                "timezone": "Asia/Shanghai"
            },
            "test": {
                "defaultTimeout": 30,
                "maxRetries": 3,
                "concurrency": 5,
                "continueOnFailure": True,
                "autoGenerateReport": True
            },
            "notification": {
                "emailEnabled": False,
                "wechatEnabled": True,
                "dingdingEnabled": False,
                "feishuEnabled": False,
                "notifyOn": ["failure", "error"]
            },
            "security": {
                "sessionTimeout": 30,
                "passwordStrength": "medium",
                "loginLockEnabled": True,
                "maxLoginAttempts": 5
            }
        }
        
        print(f"Settings data prepared: {settings_data}")
        result = RespModel.success(data=settings_data, msg="获取设置成功")
        print(f"Response model created: {result}")
        return result
    except Exception as e:
        print(f"Error in get_settings: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"获取设置失败: {str(e)}")


@router.put("/basic", response_model=ResponseModel)
async def update_basic_settings(settings: BasicSettings):
    """更新基础设置"""
    try:
        # 这里暂时只返回成功响应，实际应该保存到数据库或配置文件
        print(f"Updating basic settings: {settings}")
        return RespModel.success(data=settings.dict(), msg="基础设置更新成功")
    except Exception as e:
        raise Exception(f"更新基础设置失败: {str(e)}")


@router.put("/test", response_model=ResponseModel)
async def update_test_settings(settings: TestSettings):
    """更新测试设置"""
    try:
        print(f"Updating test settings: {settings}")
        return RespModel.success(data=settings.dict(), msg="测试设置更新成功")
    except Exception as e:
        raise Exception(f"更新测试设置失败: {str(e)}")


@router.put("/notification", response_model=ResponseModel)
async def update_notification_settings(settings: NotificationSettings):
    """更新通知设置"""
    try:
        print(f"Updating notification settings: {settings}")
        return RespModel.success(data=settings.dict(), msg="通知设置更新成功")
    except Exception as e:
        raise Exception(f"更新通知设置失败: {str(e)}")


@router.put("/security", response_model=ResponseModel)
async def update_security_settings(settings: SecuritySettings):
    """更新安全设置"""
    try:
        print(f"Updating security settings: {settings}")
        return RespModel.success(data=settings.dict(), msg="安全设置更新成功")
    except Exception as e:
        raise Exception(f"更新安全设置失败: {str(e)}")


@router.post("", response_model=ResponseModel)
async def update_all_settings(settings_data: dict):
    """更新所有设置"""
    try:
        print(f"Updating all settings: {settings_data}")
        return RespModel.success(data=settings_data, msg="设置更新成功")
    except Exception as e:
        raise Exception(f"更新设置失败: {str(e)}")
