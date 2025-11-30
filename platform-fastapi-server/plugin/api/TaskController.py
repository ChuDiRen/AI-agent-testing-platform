"""
任务调度API控制器
提供测试任务的执行、查询、取消等接口
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from core.database import get_session
from core.resp_model import respModel
from core.logger import get_logger
from ..service.TaskScheduler import task_scheduler
from ..model.PluginModel import Plugin

logger = get_logger(__name__)

# 创建路由
router = APIRouter(prefix="/Task", tags=["任务调度"])


class ExecuteTestRequest(BaseModel):
    """执行测试请求"""
    plugin_code: str = Field(..., description="执行器插件代码")
    test_case_id: int = Field(..., description="测试用例ID")
    test_case_content: str = Field(..., description="测试用例内容（YAML/JSON格式）")
    config: Optional[Dict[str, Any]] = Field(None, description="执行配置参数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "plugin_code": "web_engine",
                "test_case_id": 1,
                "test_case_content": "desc: 百度搜索测试\\nsteps:\\n  - 打开浏览器:\\n      关键字: open_browser",
                "config": {
                    "browser": "chrome",
                    "headless": False
                }
            }
        }


class TaskStatusQuery(BaseModel):
    """任务状态查询"""
    plugin_code: str = Field(..., description="插件代码")
    task_id: str = Field(..., description="任务ID")
    temp_dir: str = Field(..., description="任务临时目录")


@router.post("/execute", summary="执行测试任务")
async def execute_test(
    request: ExecuteTestRequest,
    session: Session = Depends(get_session)
):
    """
    执行测试任务
    
    调用指定的执行器插件执行测试用例
    """
    try:
        result = await task_scheduler.execute_test(
            session=session,
            plugin_code=request.plugin_code,
            test_case_id=request.test_case_id,
            test_case_content=request.test_case_content,
            config=request.config
        )
        
        if result.get("success"):
            return respModel.ok_resp(obj=result, msg="任务已提交执行")
        else:
            return respModel.error_resp(msg=result.get("error", "执行失败"))
    
    except Exception as e:
        return respModel.error_resp(msg=f"执行异常: {str(e)}")


@router.post("/status", summary="查询任务状态")
async def get_task_status(
    query: TaskStatusQuery,
    session: Session = Depends(get_session)
):
    """查询测试任务状态"""
    try:
        result = await task_scheduler.get_task_status(
            session=session,
            plugin_code=query.plugin_code,
            task_id=query.task_id,
            temp_dir=query.temp_dir
        )
        
        if result.get("success"):
            return respModel.ok_resp(obj=result.get("data"))
        else:
            return respModel.error_resp(msg=result.get("error", "查询失败"))
    
    except Exception as e:
        return respModel.error_resp(msg=f"查询异常: {str(e)}")


@router.post("/report", summary="获取测试报告")
async def get_test_report(
    query: TaskStatusQuery,
    session: Session = Depends(get_session)
):
    """获取测试报告"""
    try:
        result = await task_scheduler.get_test_report(
            session=session,
            plugin_code=query.plugin_code,
            task_id=query.task_id
        )
        
        if result.get("success"):
            return respModel.ok_resp(obj=result.get("data"))
        else:
            return respModel.error_resp(msg=result.get("error", "获取报告失败"))
    
    except Exception as e:
        return respModel.error_resp(msg=f"获取报告异常: {str(e)}")


@router.post("/cancel", summary="取消任务")
async def cancel_task(
    query: TaskStatusQuery,
    session: Session = Depends(get_session)
):
    """取消正在执行的任务"""
    try:
        result = await task_scheduler.cancel_task(
            session=session,
            plugin_code=query.plugin_code,
            task_id=query.task_id
        )
        
        if result.get("success"):
            return respModel.ok_resp(msg="任务已取消")
        else:
            return respModel.error_resp(msg=result.get("error", "取消失败"))
    
    except Exception as e:
        return respModel.error_resp(msg=f"取消异常: {str(e)}")


@router.get("/executors", summary="获取可用执行器列表")
async def list_executors(
    session: Session = Depends(get_session)
):
    """
    获取所有可用的执行器插件列表
    - 只返回 plugin_type='executor' 且 is_enabled=1 的记录
    """
    try:
        # 直接查询 Plugin 表，不再通过 TaskScheduler
        plugins = session.exec(
            select(Plugin)
            .where(Plugin.plugin_type == "executor")
            .where(Plugin.is_enabled == 1)
        ).all()

        executors = [{
            "plugin_code": p.plugin_code,
            "plugin_name": p.plugin_name,
            "version": p.version,
            "command": p.command,
            "capabilities": p.capabilities,
            "description": p.description,
        } for p in plugins]

        logger.info(f"list_executors: 查询到 {len(executors)} 个执行器")

        return respModel.ok_resp_listdata(lst=executors)
    except Exception as e:
        logger.error(f"查询执行器失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"查询异常: {str(e)}")
