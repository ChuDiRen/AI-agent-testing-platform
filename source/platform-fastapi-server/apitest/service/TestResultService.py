"""测试结果处理服务"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session, select
from apitest.model.ApiTestHistoryModel import ApiTestHistory
from apitest.service.ApiEngineService import ApiEngineService

class TestResultService:
    """测试结果处理和allure报告解析"""
    
    @staticmethod
    def save_test_result(
        db: Session,
        api_info_id: int,
        execution_result: Dict[str, Any],
        allure_results: Optional[Dict[str, Any]] = None,
        yaml_content: Optional[str] = None
    ) -> ApiTestHistory:
        """
        保存测试结果到历史记录
        
        Args:
            db: 数据库会话
            api_info_id: 接口信息ID
            execution_result: 执行结果
            allure_results: Allure解析结果
            yaml_content: YAML用例内容
            
        Returns:
            保存的测试历史记录
        """
        # 提取响应数据
        response_data = None
        if allure_results:
            response_data = ApiEngineService.extract_response_data(allure_results)
        
        # 创建历史记录
        history = ApiTestHistory(
            api_info_id=api_info_id,
            test_name=f"接口测试_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            request_url=None,  # 可以从api_info中获取
            request_method=None,  # 可以从api_info中获取
            request_headers=None,
            request_params=None,
            request_body=None,
            response_status_code=response_data.get('status_code') if response_data else None,
            response_time=int(response_data.get('response_time', 0)) if response_data else None,
            response_headers=response_data.get('response_headers') if response_data else None,
            response_body=response_data.get('response_body') if response_data else None,
            test_result='pass' if execution_result.get('success') else 'fail',
            error_message=execution_result.get('error_message') or (response_data.get('error_message') if response_data else None),
            execution_duration=execution_result.get('duration'),
            allure_report_path=None,  # 可以保存报告相对路径
            yaml_content=yaml_content,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return history
    
    @staticmethod
    def get_test_history(
        db: Session,
        api_info_id: Optional[int] = None,
        limit: int = 100
    ) -> list[ApiTestHistory]:
        """
        获取测试历史记录
        
        Args:
            db: 数据库会话
            api_info_id: 接口信息ID，如果为None则获取所有
            limit: 限制数量
            
        Returns:
            测试历史记录列表
        """
        query = select(ApiTestHistory)
        
        if api_info_id is not None:
            query = query.where(ApiTestHistory.api_info_id == api_info_id)
        
        query = query.order_by(ApiTestHistory.create_time.desc()).limit(limit)
        
        results = db.exec(query).all()
        return list(results)
    
    @staticmethod
    def get_test_statistics(
        db: Session,
        api_info_id: Optional[int] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取测试统计信息
        
        Args:
            db: 数据库会话
            api_info_id: 接口信息ID
            days: 统计天数
            
        Returns:
            统计信息字典
        """
        from datetime import timedelta
        
        query = select(ApiTestHistory)
        
        if api_info_id is not None:
            query = query.where(ApiTestHistory.api_info_id == api_info_id)
        
        # 限制时间范围
        start_date = datetime.now() - timedelta(days=days)
        query = query.where(ApiTestHistory.create_time >= start_date)
        
        results = db.exec(query).all()
        
        total = len(results)
        passed = sum(1 for r in results if r.test_result == 'pass')
        failed = sum(1 for r in results if r.test_result == 'fail')
        
        # 计算平均响应时间
        response_times = [r.response_time for r in results if r.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        statistics = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': round(passed / total * 100, 2) if total > 0 else 0,
            'avg_response_time': round(avg_response_time, 2),
            'days': days
        }
        
        return statistics
