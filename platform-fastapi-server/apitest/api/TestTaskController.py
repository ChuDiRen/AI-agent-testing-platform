import json
import uuid
from datetime import datetime

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiCollectionInfoModel import ApiCollectionInfo
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.TestTaskModel import TestTask, TestTaskExecution
from ..service.TestTaskService import TestTaskService
from ..schemas.TestTaskSchema import (
    TestTaskQuery, TestTaskCreate, TestTaskUpdate,
    TestTaskExecuteRequest, TestTaskExecutionQuery
)

logger = get_logger(__name__)

module_name = "TestTask"
module_model = TestTask
module_route = APIRouter(prefix=f"/{module_name}", tags=["测试任务管理"])


@module_route.post("/queryByPage", summary="分页查询测试任务", dependencies=[Depends(check_permission("apitest:task:query"))])
async def queryByPage(query: TestTaskQuery, session: Session = Depends(get_session)):
    """分页查询测试任务"""
    try:
        datas, total = TestTaskService.query_by_page(session, query)

        result_list = []
        for data in datas:
            # 解析case_ids
            case_ids = []
            if data.case_ids:
                try:
                    case_ids = json.loads(data.case_ids)
                except:
                    pass

            # 获取关联计划名称
            plan_name = None
            if data.plan_id:
                plan = session.get(ApiCollectionInfo, data.plan_id)
                plan_name = plan.plan_name if plan else None

            item = {
                "id": data.id,
                "project_id": data.project_id,
                "task_name": data.task_name,
                "task_desc": data.task_desc,
                "task_type": data.task_type,
                "cron_expression": data.cron_expression,
                "plan_id": data.plan_id,
                "plan_name": plan_name,
                "case_ids": case_ids,
                "case_count": len(case_ids) if case_ids else 0,
                "task_status": data.task_status,
                "last_run_time": TimeFormatter.format_datetime(data.last_run_time) if data.last_run_time else None,
                "next_run_time": TimeFormatter.format_datetime(data.next_run_time) if data.next_run_time else None,
                "run_count": data.run_count,
                "success_count": data.success_count,
                "fail_count": data.fail_count,
                "create_time": TimeFormatter.format_datetime(data.create_time),
                "update_time": TimeFormatter.format_datetime(data.update_time)
            }
            result_list.append(item)

        return respModel.ok_resp_list(lst=result_list, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryById", summary="根据ID查询测试任务", dependencies=[Depends(check_permission("apitest:task:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询测试任务详情"""
    try:
        task = TestTaskService.query_by_id(session, id)
        if not task:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 解析JSON字段
        case_ids = []
        if task.case_ids:
            try:
                case_ids = json.loads(task.case_ids)
            except:
                pass
        
        notify_config = {}
        if task.notify_config:
            try:
                notify_config = json.loads(task.notify_config)
            except:
                pass
        
        extra_config = {}
        if task.extra_config:
            try:
                extra_config = json.loads(task.extra_config)
            except:
                pass
        
        # 获取关联计划信息
        plan_info = None
        if task.plan_id:
            plan = session.get(ApiCollectionInfo, task.plan_id)
            if plan:
                plan_info = {
                    "id": plan.id,
                    "plan_name": plan.plan_name,
                    "plan_desc": plan.plan_desc
                }
        
        # 获取关联用例信息
        cases_info = []
        for case_id in case_ids:
            case = session.get(ApiInfoCase, case_id)
            if case:
                cases_info.append({
                    "id": case.id,
                    "case_name": case.case_name,
                    "case_desc": case.case_desc
                })
        
        result = {
            "id": task.id,
            "project_id": task.project_id,
            "task_name": task.task_name,
            "task_desc": task.task_desc,
            "task_type": task.task_type,
            "cron_expression": task.cron_expression,
            "plan_id": task.plan_id,
            "plan_info": plan_info,
            "case_ids": case_ids,
            "cases_info": cases_info,
            "task_status": task.task_status,
            "last_run_time": TimeFormatter.format_datetime(task.last_run_time) if task.last_run_time else None,
            "next_run_time": TimeFormatter.format_datetime(task.next_run_time) if task.next_run_time else None,
            "run_count": task.run_count,
            "success_count": task.success_count,
            "fail_count": task.fail_count,
            "notify_config": notify_config,
            "extra_config": extra_config,
            "create_by": task.create_by,
            "create_time": TimeFormatter.format_datetime(task.create_time),
            "update_time": TimeFormatter.format_datetime(task.update_time)
        }
        
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/insert", summary="新增测试任务", dependencies=[Depends(check_permission("apitest:task:add"))])
async def insert(data: TestTaskCreate, session: Session = Depends(get_session)):
    """新增测试任务"""
    try:
        task = module_model(
            project_id=data.project_id,
            task_name=data.task_name,
            task_desc=data.task_desc,
            task_type=data.task_type,
            cron_expression=data.cron_expression,
            plan_id=data.plan_id,
            case_ids=json.dumps(data.case_ids, ensure_ascii=False) if data.case_ids else None,
            task_status='pending',
            notify_config=json.dumps(data.notify_config, ensure_ascii=False) if data.notify_config else None,
            extra_config=json.dumps(data.extra_config, ensure_ascii=False) if data.extra_config else None,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        session.add(task)
        session.commit()

        # 如果是定时任务，添加到调度器
        if task.task_type == 'scheduled' and task.cron_expression:
            try:
                from apitest.service.cron_scheduler import cron_scheduler
                cron_scheduler.add_task(task.id, task.cron_expression)
            except Exception as e:
                logger.warning(f"添加定时任务到调度器失败: {e}")

        return respModel.ok_resp_text(msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.put("/update", summary="更新测试任务", dependencies=[Depends(check_permission("apitest:task:edit"))])
async def update(data: TestTaskUpdate, session: Session = Depends(get_session)):
    """更新测试任务"""
    try:
        task = session.get(module_model, data.id)
        if not task:
            return respModel.error_resp("任务不存在")
        
        if data.project_id is not None:
            task.project_id = data.project_id
        if data.task_name is not None:
            task.task_name = data.task_name
        if data.task_desc is not None:
            task.task_desc = data.task_desc
        if data.task_type is not None:
            task.task_type = data.task_type
        if data.cron_expression is not None:
            task.cron_expression = data.cron_expression
        if data.plan_id is not None:
            task.plan_id = data.plan_id
        if data.case_ids is not None:
            task.case_ids = json.dumps(data.case_ids, ensure_ascii=False) if data.case_ids else None
        if data.task_status is not None:
            task.task_status = data.task_status
        if data.notify_config is not None:
            task.notify_config = json.dumps(data.notify_config, ensure_ascii=False) if data.notify_config else None
        if data.extra_config is not None:
            task.extra_config = json.dumps(data.extra_config, ensure_ascii=False) if data.extra_config else None
        
        task.update_time = datetime.now()
        session.commit()

        # 同步更新调度器
        if task.task_type == 'scheduled' and task.cron_expression:
            try:
                from apitest.service.cron_scheduler import cron_scheduler
                cron_scheduler.add_task(task.id, task.cron_expression)
            except Exception as e:
                logger.warning(f"更新定时任务调度失败: {e}")
        elif task.task_type != 'scheduled':
            # 移除定时任务
            try:
                from apitest.service.cron_scheduler import cron_scheduler
                cron_scheduler.remove_task(task.id)
            except Exception as e:
                logger.warning(f"移除定时任务调度失败: {e}")

        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.delete("/delete", summary="删除测试任务", dependencies=[Depends(check_permission("apitest:task:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除测试任务"""
    try:
        obj = session.get(module_model, id)
        if obj:
            session.delete(obj)
            session.commit()

            # 从调度器移除
            try:
                from apitest.service.cron_scheduler import cron_scheduler
                cron_scheduler.remove_task(id)
            except Exception as e:
                logger.warning(f"从调度器移除任务失败: {e}")

            return respModel.ok_resp_text(msg="删除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/execute", summary="执行测试任务", dependencies=[Depends(check_permission("apitest:task:execute"))])
async def execute(request: TestTaskExecuteRequest, session: Session = Depends(get_session)):
    """执行测试任务"""
    from ..service.execution_service import ExecutionService
    
    try:
        task = session.get(module_model, request.task_id)
        if not task:
            return respModel.error_resp("任务不存在")
        
        if task.task_status == 'disabled':
            return respModel.error_resp("任务已禁用，无法执行")
        
        # 创建执行记录
        execution_uuid = str(uuid.uuid4())
        execution = TestTaskExecution(
            task_id=task.id,
            execution_uuid=execution_uuid,
            trigger_type=request.trigger_type,
            status='running',
            start_time=datetime.now(),
            create_time=datetime.now()
        )
        session.add(execution)
        session.flush()
        
        # 更新任务状态
        task.task_status = 'running'
        task.last_run_time = datetime.now()
        task.run_count += 1
        
        exec_service = ExecutionService(session)

        # 根据任务配置执行
        total_cases = 0
        if task.plan_id:
            # 执行测试计划
            result = exec_service.execute_plan(
                plan_id=task.plan_id,
                test_name=f"{task.task_name}_{execution_uuid[:8]}",
                task_execution_id=execution.id
            )
            total_cases = result.get('total_cases', 0)
        elif task.case_ids:
            # 执行指定用例
            case_ids = json.loads(task.case_ids) if task.case_ids else []
            for idx, case_id in enumerate(case_ids):
                # 只有第一个用例传递 task_execution_id，避免重复更新
                exec_service.execute_case(
                    case_id=case_id,
                    test_name=f"{task.task_name}_{case_id}_{execution_uuid[:8]}",
                    context_vars=request.context_vars,
                    task_execution_id=execution.id if idx == len(case_ids) - 1 else None
                )
            total_cases = len(case_ids)
        else:
            return respModel.error_resp("任务未配置测试计划或用例")
        
        # 更新执行记录
        execution.total_cases = total_cases
        
        session.commit()
        
        return respModel.ok_resp(dic_t={
            "execution_id": execution.id,
            "execution_uuid": execution_uuid,
            "total_cases": total_cases,
            "status": "running"
        }, msg="任务已提交执行")
    except Exception as e:
        session.rollback()
        logger.error(f"执行失败: {e}", exc_info=True)
        return respModel.error_resp(f"执行失败: {str(e)}")


@module_route.put("/updateStatus", summary="更新任务状态", dependencies=[Depends(check_permission("apitest:task:edit"))])
async def updateStatus(id: int = Query(...), status: str = Query(...), session: Session = Depends(get_session)):
    """更新任务状态（启用/禁用）"""
    try:
        task = session.get(module_model, id)
        if not task:
            return respModel.error_resp("任务不存在")
        
        if status not in ['pending', 'disabled']:
            return respModel.error_resp("无效的状态值")
        
        task.task_status = status
        task.update_time = datetime.now()
        session.commit()
        
        return respModel.ok_resp_text(msg="状态更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/queryExecutions", summary="查询任务执行记录", dependencies=[Depends(check_permission("apitest:task:query"))])
async def queryExecutions(query: TestTaskExecutionQuery, session: Session = Depends(get_session)):
    """查询任务执行记录"""
    try:
        statement = select(TestTaskExecution)
        if query.task_id:
            statement = statement.where(TestTaskExecution.task_id == query.task_id)
        if query.status:
            statement = statement.where(TestTaskExecution.status == query.status)
        if query.trigger_type:
            statement = statement.where(TestTaskExecution.trigger_type == query.trigger_type)

        offset = (query.page - 1) * query.pageSize
        datas = session.exec(statement.order_by(TestTaskExecution.create_time.desc()).limit(query.pageSize).offset(offset)).all()
        total = len(session.exec(statement).all())
        
        result_list = []
        for data in datas:
            # 获取任务名称
            task = session.get(TestTask, data.task_id)
            task_name = task.task_name if task else None
            
            item = {
                "id": data.id,
                "task_id": data.task_id,
                "task_name": task_name,
                "execution_uuid": data.execution_uuid,
                "trigger_type": data.trigger_type,
                "status": data.status,
                "total_cases": data.total_cases,
                "passed_cases": data.passed_cases,
                "failed_cases": data.failed_cases,
                "skipped_cases": data.skipped_cases,
                "start_time": TimeFormatter.format_datetime(data.start_time) if data.start_time else None,
                "end_time": TimeFormatter.format_datetime(data.end_time) if data.end_time else None,
                "duration": data.duration,
                "report_path": data.report_path,
                "error_message": data.error_message,
                "create_time": TimeFormatter.format_datetime(data.create_time)
            }
            result_list.append(item)
        
        return respModel.ok_resp_list(lst=result_list, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/getExecutionDetail", summary="获取执行记录详情", dependencies=[Depends(check_permission("apitest:task:query"))])
async def getExecutionDetail(id: int = Query(...), session: Session = Depends(get_session)):
    """获取执行记录详情"""
    try:
        execution = session.get(TestTaskExecution, id)
        if not execution:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 获取任务信息
        task = session.get(TestTask, execution.task_id)
        
        result = {
            "id": execution.id,
            "task_id": execution.task_id,
            "task_name": task.task_name if task else None,
            "execution_uuid": execution.execution_uuid,
            "trigger_type": execution.trigger_type,
            "status": execution.status,
            "total_cases": execution.total_cases,
            "passed_cases": execution.passed_cases,
            "failed_cases": execution.failed_cases,
            "skipped_cases": execution.skipped_cases,
            "start_time": TimeFormatter.format_datetime(execution.start_time) if execution.start_time else None,
            "end_time": TimeFormatter.format_datetime(execution.end_time) if execution.end_time else None,
            "duration": execution.duration,
            "report_path": execution.report_path,
            "error_message": execution.error_message,
            "create_time": TimeFormatter.format_datetime(execution.create_time)
        }
        
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
