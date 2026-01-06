"""
API测试Controller - 提供API测试执行相关接口
"""
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..schemas.ApiTestSchema import ApiTestExecuteRequest, ApiTestResult, EngineHealthResponse
from ..service.ApiTestService import ApiTestService

module_name = "ApiTest"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试执行"])
logger = get_logger(__name__)


@module_route.post("/execute", summary="执行API测试", dependencies=[Depends(check_permission("apitest:test:execute"))])
async def execute_test(request: ApiTestExecuteRequest, session: Session = Depends(get_session)):
    """
    执行API测试
    
    Args:
        request: 测试执行请求参数
        session: 数据库会话
        
    Returns:
        包含测试ID的响应数据
    """
    try:
        result = ApiTestService.execute_test(session, request)
        return respModel.ok_resp(obj=result, msg="测试执行已启动")
    except Exception as e:
        logger.error(f"执行API测试失败: {e}", exc_info=True)
        return respModel.error_resp(f"测试执行失败: {e}")


@module_route.get("/status", summary="查询测试状态", dependencies=[Depends(check_permission("apitest:test:query"))])
async def get_test_status(test_id: int = Query(..., description="测试ID"), session: Session = Depends(get_session)):
    """
    查询测试执行状态
    
    Args:
        test_id: 测试ID
        session: 数据库会话
        
    Returns:
        测试状态信息
    """
    try:
        result = ApiTestService.get_test_status(session, test_id)
        if result:
            return respModel.ok_resp(obj=result, msg="查询成功")
        else:
            return respModel.error_resp("测试记录不存在")
    except Exception as e:
        logger.error(f"查询测试状态失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")


@module_route.get("/engine/health", summary="检查测试引擎健康状态", dependencies=[Depends(check_permission("apitest:test:query"))])
async def check_engine_health():
    """
    检查API测试引擎健康状态
    
    Returns:
        引擎健康状态信息
    """
    try:
        result = ApiTestService.check_engine_health()
        if result["status"] == "healthy":
            return respModel.ok_resp(obj=result, msg="引擎状态正常")
        else:
            return respModel.error_resp(result.get("message", "引擎状态异常"))
    except Exception as e:
        logger.error(f"检查引擎健康状态失败: {e}", exc_info=True)
        return respModel.error_resp(f"检查失败: {e}")
