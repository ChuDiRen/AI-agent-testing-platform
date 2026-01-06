"""
API测试Service层
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from core.logger import get_logger
from sqlmodel import Session, select

from ..model.ApiHistoryModel import ApiHistory
from ..model.ApiInfoModel import ApiInfo
from ..schemas.ApiTestSchema import ApiTestExecuteRequest, ApiTestResult

logger = get_logger(__name__)


class ApiTestService:
    """API测试服务类"""
    
    @staticmethod
    def execute_test(session: Session, request: ApiTestExecuteRequest) -> Dict[str, Any]:
        """
        执行API测试
        
        Args:
            session: 数据库会话
            request: 测试执行请求
            
        Returns:
            Dict: 包含test_id的响应数据
        """
        try:
            # 查询API信息获取project_id
            api_info = session.get(ApiInfo, request.api_info_id)
            if not api_info:
                raise ValueError(f"API信息不存在，ID: {request.api_info_id}")
            
            # 生成测试ID
            test_id = ApiTestService._generate_test_id()
            
            # 创建测试历史记录
            history = ApiHistory(
                api_info_id=request.api_info_id,
                project_id=api_info.project_id,  # 从API信息中获取project_id
                test_name=request.test_name or f"API测试_{test_id}",
                test_status="running",
                request_data=json.dumps({
                    "context_vars": request.context_vars,
                    "pre_script": request.pre_script,
                    "post_script": request.post_script,
                    "variable_extracts": [vars(item) for item in request.variable_extracts],
                    "assertions": request.assertions
                }, ensure_ascii=False),
                create_time=datetime.now()
            )
            
            session.add(history)
            session.commit()
            session.refresh(history)
            
            # TODO: 这里应该调用实际的测试执行引擎
            # 目前先返回模拟数据
            logger.info(f"API测试已启动，test_id: {test_id}, history_id: {history.id}")
            
            return {
                "test_id": test_id,
                "history_id": history.id,
                "status": "running"
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"执行API测试失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_test_status(session: Session, test_id: int) -> Optional[ApiTestResult]:
        """
        获取测试状态
        
        Args:
            session: 数据库会话
            test_id: 测试ID
            
        Returns:
            ApiTestResult: 测试结果
        """
        try:
            # 根据test_id查询历史记录
            # 这里简化处理，实际应该有更好的关联方式
            statement = select(ApiHistory).where(
                ApiHistory.test_name.like(f"%API测试_{test_id}%")
            ).order_by(ApiHistory.create_time.desc())
            
            history = session.exec(statement).first()
            
            if not history:
                return None
            
            # 解析响应数据
            response_data = None
            if history.response_data:
                try:
                    response_data = json.loads(history.response_data)
                except json.JSONDecodeError:
                    response_data = {"raw": history.response_data}
            
            return ApiTestResult(
                test_id=test_id,
                test_status=history.test_status,
                response_time=history.response_time,
                status_code=history.status_code,
                response_data=response_data,
                error_message=history.error_message,
                allure_report_url=f"/api/reports/allure/{test_id}/index.html" if history.allure_report_path else None
            )
            
        except Exception as e:
            logger.error(f"获取测试状态失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def check_engine_health() -> Dict[str, Any]:
        """
        检查测试引擎健康状态
        
        Returns:
            Dict: 引擎健康状态
        """
        try:
            # TODO: 实际检查测试引擎状态
            # 目前返回模拟数据
            return {
                "status": "healthy",
                "message": "API测试引擎运行正常",
                "version": "1.0.0"
            }
        except Exception as e:
            logger.error(f"检查引擎健康状态失败: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "message": f"引擎检查失败: {str(e)}"
            }
    
    @staticmethod
    def _generate_test_id() -> int:
        """生成测试ID"""
        # 简单的ID生成策略，实际项目中可能需要更复杂的逻辑
        return int(datetime.now().timestamp() * 1000) % 1000000
