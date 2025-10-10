# Copyright (c) 2025 左岚. All rights reserved.
"""
API引擎执行任务
"""
from app.core.celery_app import celery_app
from datetime import datetime
import asyncio


@celery_app.task(bind=True, name="api_engine.execute_case")
def execute_case_task(
    self,
    case_id: int,
    context: dict,
    execution_id: int,
    user_id: int
):
    """
    异步执行测试用例
    
    Args:
        self: Celery任务实例
        case_id: 用例ID
        context: 执行上下文
        execution_id: 执行记录ID
        user_id: 执行用户ID
    
    Returns:
        执行结果
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from ..services.executor import ApiEngineExecutor
    from ..services.case_service import CaseService
    from ..models.execution import ApiEngineExecution
    import time
    
    # 创建同步数据库会话
    engine = create_engine(str(settings.DATABASE_URL).replace('+aiosqlite', ''))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 更新状态为running
        self.update_state(state='RUNNING', meta={'progress': 10, 'message': '开始执行'})
        
        # 获取用例
        case = db.query(__import__('app.plugins.api_engine.models.case', fromlist=['ApiEngineCase']).ApiEngineCase).filter_by(case_id=case_id).first()
        if not case:
            raise ValueError(f"用例不存在: {case_id}")
        
        # 初始化执行器
        executor = ApiEngineExecutor()
        
        # 生成YAML内容
        self.update_state(state='RUNNING', meta={'progress': 20, 'message': '准备用例'})
        
        if case.config_type == 'yaml':
            yaml_content = case.yaml_content
        else:
            yaml_content = executor.form_to_yaml(case.config_data or {})
        
        # 合并全局变量
        suite = db.query(__import__('app.plugins.api_engine.models.suite', fromlist=['ApiEngineSuite']).ApiEngineSuite).filter_by(suite_id=case.suite_id).first()
        execution_context = suite.global_context or {} if suite else {}
        execution_context.update(context or {})
        
        # 执行用例
        self.update_state(state='RUNNING', meta={'progress': 40, 'message': '执行中'})
        
        start_time = time.time()
        result = executor.execute_case(yaml_content, execution_context)
        duration = time.time() - start_time
        
        # 更新执行记录
        self.update_state(state='RUNNING', meta={'progress': 80, 'message': '保存结果'})

        execution = db.query(ApiEngineExecution).filter_by(execution_id=execution_id).first()
        if execution:
            execution.status = result['status']
            execution.result = result.get('response_data')
            execution.logs = result.get('logs', '')
            execution.error_message = result.get('error_message')
            execution.duration = duration
            execution.finished_at = datetime.now()

            # 添加详细执行信息
            execution.step_results = result.get('step_results', [])
            execution.execution_context = result.get('context', {})
            execution.start_time = result.get('start_time')
            execution.end_time = result.get('end_time')
            execution.execution_time = result.get('execution_time')

            # 生成执行报告
            from ..services.report_service import ReportService
            case_info = {
                "case_id": case_id,
                "name": case.name if case else "未知用例",
                "suite_name": suite.name if suite else "未知套件",
                "executed_by": user_id
            }
            execution_report = ReportService.generate_execution_report(result, case_info)
            execution.report_data = execution_report

            db.commit()

        self.update_state(state='SUCCESS', meta={'progress': 100, 'message': '执行完成'})

        return {
            'status': result['status'],
            'execution_id': execution_id,
            'duration': duration,
            'step_count': len(result.get('step_results', [])),
            'message': '执行完成'
        }
        
    except Exception as e:
        # 更新执行记录为失败
        try:
            execution = db.query(ApiEngineExecution).filter_by(execution_id=execution_id).first()
            if execution:
                execution.status = 'error'
                execution.error_message = str(e)
                execution.finished_at = datetime.now()
                db.commit()
        except:
            pass
        
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    
    finally:
        db.close()

