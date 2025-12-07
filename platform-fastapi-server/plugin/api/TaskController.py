"""
任务调度API控制器
提供测试任务的执行、查询、取消等接口
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from datetime import datetime
from core.database import get_session
from core.resp_model import respModel
from core.logger import get_logger
from ..service.TaskScheduler import task_scheduler
from ..model.PluginModel import Plugin
from apitest.model.ApiHistoryModel import ApiHistory
from apitest.model.ApiInfoCaseModel import ApiInfoCase
import json
import re

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
    
    调用指定的执行器插件执行测试用例，并保存执行历史
    """
    try:
        result = await task_scheduler.execute_test(
            session=session,
            plugin_code=request.plugin_code,
            test_case_id=request.test_case_id,
            test_case_content=request.test_case_content,
            config=request.config
        )
        
        # 保存执行历史到 ApiHistory 表
        try:
            test_status = "success" if result.get("success") else "failed"
            error_msg = result.get("error") if not result.get("success") else None
            exec_result = result.get("result", {}) or {}
            
            # 获取用例信息
            case_info = session.get(ApiInfoCase, request.test_case_id)
            project_id = case_info.project_id if case_info else 0
            case_name = case_info.case_name if case_info else f"用例_{request.test_case_id}"
            
            # 从执行结果中提取请求和响应信息
            # 执行结果结构: result.data.request / result.data.response
            request_url = None
            request_method = None
            request_headers = None
            request_params = None
            request_body = None
            response_time = None
            status_code = None
            response_body = None
            response_headers = None
            
            if isinstance(exec_result, dict):
                # 提取请求信息
                req_data = exec_result.get("request", {})
                if req_data:
                    request_url = req_data.get("url")
                    request_method = req_data.get("method")
                    request_headers = req_data.get("headers")
                    request_params = req_data.get("params")
                    request_body = req_data.get("body")
                    if request_headers is not None and not isinstance(request_headers, str):
                        request_headers = json.dumps(request_headers, ensure_ascii=False)
                    if request_params is not None and not isinstance(request_params, str):
                        request_params = json.dumps(request_params, ensure_ascii=False) if request_params else None
                    if request_body is not None and not isinstance(request_body, str):
                        request_body = json.dumps(request_body, ensure_ascii=False)
                
                # 提取响应信息
                resp_data = exec_result.get("response", {})
                if resp_data:
                    status_code = resp_data.get("status_code")
                    response_headers = resp_data.get("headers")
                    response_body = resp_data.get("body")
                    if response_headers is not None and not isinstance(response_headers, str):
                        response_headers = json.dumps(response_headers, ensure_ascii=False) if response_headers else None
                    if response_body is not None and not isinstance(response_body, str):
                        response_body = json.dumps(response_body, ensure_ascii=False)
                
                # 提取汇总信息中的耗时
                summary = exec_result.get("summary", {})
                if summary:
                    # 尝试从 duration 字符串中提取时间
                    duration_text = summary.get("duration", "")
                    if duration_text:
                        time_match = re.search(r'([\d.]+)s', duration_text)
                        if time_match:
                            response_time = int(float(time_match.group(1)) * 1000)  # 转为毫秒
            
            # 如果执行结果中没有，尝试从 YAML 中提取
            if not request_url:
                try:
                    url_match = re.search(r'url:\s*["\']?([^"\'}\n]+)', request.test_case_content)
                    if url_match:
                        request_url = url_match.group(1).strip()
                except Exception:
                    pass
            if not request_method:
                try:
                    method_match = re.search(r'method:\s*["\']?(\w+)', request.test_case_content)
                    if method_match:
                        request_method = method_match.group(1).upper()
                except Exception:
                    pass
            
            history = ApiHistory(
                api_info_id=0,
                project_id=project_id or 0,
                case_info_id=request.test_case_id,
                test_name=f"{case_name}_{datetime.now().strftime('%H%M%S')}",
                test_status=test_status,
                request_url=request_url,
                request_method=request_method,
                request_headers=request_headers,
                request_params=request_params,
                request_body=request_body,
                response_time=int(response_time) if response_time else None,
                status_code=int(status_code) if status_code else None,
                response_body=response_body,
                response_headers=response_headers,
                yaml_content=request.test_case_content,
                error_message=error_msg,
                allure_report_path=result.get("temp_dir") or None,
                create_time=datetime.now(),
                finish_time=datetime.now(),
                modify_time=datetime.now()
            )
            session.add(history)
            session.commit()
            session.refresh(history)
            
            # 将历史记录ID添加到返回结果
            result["history_id"] = history.id
            logger.info(f"测试执行历史已保存: history_id={history.id}, status={test_status}")
        except Exception as save_error:
            logger.error(f"保存执行历史失败: {save_error}", exc_info=True)
        
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
            "config_schema": p.config_schema,  # 包含参数定义
        } for p in plugins]

        logger.info(f"list_executors: 查询到 {len(executors)} 个执行器")

        return respModel.ok_resp_listdata(lst=executors)
    except Exception as e:
        logger.error(f"查询执行器失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"查询异常: {str(e)}")
