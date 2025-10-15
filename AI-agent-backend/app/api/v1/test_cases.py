"""
测试用例模块API
提供测试用例的CRUD、批量操作、AI生成和导出功能
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import pandas as pd

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.test_case_service import TestCaseService
from app.utils.log_decorators import log_user_action

router = APIRouter()


@router.get("/", summary="获取测试用例列表")
@log_user_action(action="查看", resource_type="测试用例管理", description="查看用例列表")
async def get_test_case_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="用例名称关键词"),
    module: Optional[str] = Query(None, description="所属模块"),
    priority: Optional[str] = Query(None, description="优先级"),
    test_type: Optional[str] = Query(None, description="测试类型"),
    status: Optional[str] = Query(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试用例列表（分页）"""
    try:
        test_case_service = TestCaseService(db)

        # 构建查询条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if module:
            filters['module'] = module
        if priority:
            filters['priority'] = priority
        if test_type:
            filters['test_type'] = test_type
        if status:
            filters['status'] = status

        # 获取用例列表
        test_cases, total = await test_case_service.get_test_case_list(
            page=page,
            page_size=page_size,
            filters=filters
        )

        # 构建响应数据
        test_case_list = []
        for test_case in test_cases:
            test_case_data = {
                "id": test_case.id,
                "name": test_case.name,
                "module": test_case.module,
                "description": test_case.description or "",
                "preconditions": test_case.preconditions or "",
                "test_steps": test_case.test_steps or "",
                "expected_result": test_case.expected_result or "",
                "priority": test_case.priority,
                "test_type": test_case.test_type,
                "status": test_case.status,
                "created_at": test_case.create_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.create_time else "",
                "updated_at": test_case.update_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.update_time else ""
            }
            test_case_list.append(test_case_data)

        response_data = {
            "items": test_case_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取用例列表失败: {str(e)}")


@router.get("/{test_case_id}", summary="获取单个测试用例详情")
@log_user_action(action="查看", resource_type="测试用例管理", description="查看用例详情")
async def get_test_case_detail(
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个测试用例的详细信息"""
    try:
        test_case_service = TestCaseService(db)
        test_case = await test_case_service.get_test_case_by_id(test_case_id)

        if not test_case:
            return Fail(msg="测试用例不存在")

        test_case_data = {
            "id": test_case.id,
            "name": test_case.name,
            "module": test_case.module,
            "description": test_case.description or "",
            "preconditions": test_case.preconditions or "",
            "test_steps": test_case.test_steps or "",
            "expected_result": test_case.expected_result or "",
            "priority": test_case.priority,
            "test_type": test_case.test_type,
            "status": test_case.status,
            "created_at": test_case.create_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.create_time else "",
            "updated_at": test_case.update_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.update_time else ""
        }

        return Success(data=test_case_data)

    except Exception as e:
        return Fail(msg=f"获取用例详情失败: {str(e)}")


@router.post("/", summary="创建测试用例")
@log_user_action(action="新建", resource_type="测试用例管理", description="新建测试用例")
async def create_test_case(
    name: str = Body(..., description="用例名称"),
    module: str = Body(..., description="所属模块"),
    description: Optional[str] = Body(None, description="用例描述"),
    preconditions: Optional[str] = Body(None, description="前置条件"),
    test_steps: str = Body(..., description="测试步骤"),
    expected_result: str = Body(..., description="预期结果"),
    priority: str = Body("P3", description="优先级"),
    test_type: str = Body("functional", description="测试类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的测试用例"""
    try:
        test_case_service = TestCaseService(db)

        # 创建测试用例
        new_test_case = await test_case_service.create_test_case(
            name=name,
            module=module,
            description=description,
            preconditions=preconditions,
            test_steps=test_steps,
            expected_result=expected_result,
            priority=priority,
            test_type=test_type,
            created_by=current_user.id
        )

        return Success(data={"id": new_test_case.id}, msg="创建成功")

    except Exception as e:
        return Fail(msg=f"创建测试用例失败: {str(e)}")


@router.put("/{test_case_id}", summary="更新测试用例")
@log_user_action(action="编辑", resource_type="测试用例管理", description="编辑测试用例")
async def update_test_case(
    test_case_id: int,
    name: Optional[str] = Body(None, description="用例名称"),
    module: Optional[str] = Body(None, description="所属模块"),
    description: Optional[str] = Body(None, description="用例描述"),
    preconditions: Optional[str] = Body(None, description="前置条件"),
    test_steps: Optional[str] = Body(None, description="测试步骤"),
    expected_result: Optional[str] = Body(None, description="预期结果"),
    priority: Optional[str] = Body(None, description="优先级"),
    test_type: Optional[str] = Body(None, description="测试类型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新测试用例信息"""
    try:
        test_case_service = TestCaseService(db)

        # 检查测试用例是否存在
        test_case = await test_case_service.get_test_case_by_id(test_case_id)
        if not test_case:
            return Fail(msg="测试用例不存在")

        # 更新测试用例
        await test_case_service.update_test_case(
            test_case_id=test_case_id,
            name=name,
            module=module,
            description=description,
            preconditions=preconditions,
            test_steps=test_steps,
            expected_result=expected_result,
            priority=priority,
            test_type=test_type,
            updated_by=current_user.id
        )

        return Success(msg="更新成功")

    except Exception as e:
        return Fail(msg=f"更新测试用例失败: {str(e)}")


@router.delete("/{test_case_id}", summary="删除测试用例")
@log_user_action(action="删除", resource_type="测试用例管理", description="删除测试用例")
async def delete_test_case(
    test_case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除测试用例"""
    try:
        test_case_service = TestCaseService(db)

        # 检查测试用例是否存在
        test_case = await test_case_service.get_test_case_by_id(test_case_id)
        if not test_case:
            return Fail(msg="测试用例不存在")

        # 删除测试用例
        await test_case_service.delete_test_case(test_case_id)

        return Success(msg="删除成功")

    except Exception as e:
        return Fail(msg=f"删除测试用例失败: {str(e)}")


@router.post("/{test_case_id}/execute", summary="执行测试用例")
@log_user_action(action="执行", resource_type="测试用例管理", description="执行测试用例")
async def execute_test_case(
    test_case_id: int,
    agent_id: Optional[int] = Body(None, description="执行代理ID"),
    environment: Optional[str] = Body(None, description="执行环境"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """执行单个测试用例"""
    try:
        test_case_service = TestCaseService(db)

        # 检查测试用例是否存在
        test_case = await test_case_service.get_test_case_by_id(test_case_id)
        if not test_case:
            return Fail(msg="测试用例不存在")

        # 执行测试用例
        execution_result = await test_case_service.execute_test_case(
            test_case_id=test_case_id,
            agent_id=agent_id,
            environment=environment,
            executed_by=current_user.id
        )

        return Success(data=execution_result, msg="测试用例执行成功")

    except Exception as e:
        return Fail(msg=f"执行测试用例失败: {str(e)}")


@router.post("/batch/execute", summary="批量执行测试用例")
@log_user_action(action="批量执行", resource_type="测试用例管理", description="批量执行测试用例")
async def batch_execute_test_cases(
    test_case_ids: List[int] = Body(..., description="测试用例ID列表"),
    agent_id: Optional[int] = Body(None, description="执行代理ID"),
    environment: Optional[str] = Body(None, description="执行环境"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量执行测试用例"""
    try:
        test_case_service = TestCaseService(db)

        if not test_case_ids:
            return Fail(msg="请选择要执行的测试用例")

        # 执行批量操作
        success_count, error_messages, results = await test_case_service.batch_execute_test_cases(
            test_case_ids=test_case_ids,
            agent_id=agent_id,
            environment=environment,
            executed_by=current_user.id
        )

        if error_messages:
            return Success(
                data={
                    "success_count": success_count,
                    "errors": error_messages,
                    "results": results
                },
                msg=f"批量执行完成，成功 {success_count} 个，失败 {len(error_messages)} 个"
            )
        else:
            return Success(
                data={
                    "success_count": success_count,
                    "results": results
                },
                msg=f"批量执行完成，成功执行 {success_count} 个测试用例"
            )

    except Exception as e:
        return Fail(msg=f"批量执行失败: {str(e)}")


@router.post("/batch/delete", summary="批量删除测试用例")
@log_user_action(action="批量删除", resource_type="测试用例管理", description="批量删除测试用例")
async def batch_delete_test_cases(
    test_case_ids: List[int] = Body(..., description="测试用例ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量删除测试用例"""
    try:
        test_case_service = TestCaseService(db)

        if not test_case_ids:
            return Fail(msg="请选择要删除的测试用例")

        # 执行批量删除
        success_count, error_messages = await test_case_service.batch_delete_test_cases(
            test_case_ids=test_case_ids,
            deleted_by=current_user.id
        )

        if error_messages:
            return Success(
                data={"success_count": success_count, "errors": error_messages},
                msg=f"批量删除完成，成功 {success_count} 个，失败 {len(error_messages)} 个"
            )
        else:
            return Success(
                data={"success_count": success_count},
                msg=f"批量删除完成，成功删除 {success_count} 个测试用例"
            )

    except Exception as e:
        return Fail(msg=f"批量删除失败: {str(e)}")


@router.post("/batch/create", summary="批量创建测试用例")
@log_user_action(action="批量创建", resource_type="测试用例管理", description="批量创建测试用例")
async def batch_create_test_cases(
    test_cases: List[Dict[str, Any]] = Body(..., description="测试用例数据列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量创建测试用例（主要用于AI生成的用例保存）"""
    try:
        test_case_service = TestCaseService(db)

        if not test_cases:
            return Fail(msg="请提供要创建的测试用例数据")

        # 批量创建测试用例
        success_count, error_messages, created_ids = await test_case_service.batch_create_test_cases(
            test_cases=test_cases,
            created_by=current_user.id
        )

        if error_messages:
            return Success(
                data={
                    "success_count": success_count,
                    "errors": error_messages,
                    "created_ids": created_ids
                },
                msg=f"批量创建完成，成功 {success_count} 个，失败 {len(error_messages)} 个"
            )
        else:
            return Success(
                data={
                    "success_count": success_count,
                    "created_ids": created_ids
                },
                msg=f"批量创建完成，成功创建 {success_count} 个测试用例"
            )

    except Exception as e:
        return Fail(msg=f"批量创建失败: {str(e)}")


@router.get("/export", summary="导出测试用例数据")
@log_user_action(action="导出", resource_type="测试用例管理", description="导出测试用例数据")
async def export_test_cases(
    keyword: Optional[str] = Query(None, description="用例名称关键词"),
    module: Optional[str] = Query(None, description="所属模块"),
    priority: Optional[str] = Query(None, description="优先级"),
    test_type: Optional[str] = Query(None, description="测试类型"),
    status: Optional[str] = Query(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出测试用例数据为Excel文件"""
    try:
        test_case_service = TestCaseService(db)

        # 构建查询条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if module:
            filters['module'] = module
        if priority:
            filters['priority'] = priority
        if test_type:
            filters['test_type'] = test_type
        if status:
            filters['status'] = status

        # 获取所有符合条件的测试用例（不分页）
        test_cases = await test_case_service.get_all_test_cases(filters=filters)

        # 构建导出数据
        export_data = []
        for test_case in test_cases:
            export_data.append({
                "ID": test_case.id,
                "用例名称": test_case.name,
                "所属模块": test_case.module,
                "用例描述": test_case.description or "",
                "前置条件": test_case.preconditions or "",
                "测试步骤": test_case.test_steps or "",
                "预期结果": test_case.expected_result or "",
                "优先级": test_case.priority,
                "测试类型": test_case.test_type,
                "状态": test_case.status,
                "创建时间": test_case.create_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.create_time else "",
                "更新时间": test_case.update_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.update_time else ""
            })

        # 创建Excel文件
        df = pd.DataFrame(export_data)
        
        # 使用内存缓冲区
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='测试用例列表', index=False)
        
        output.seek(0)

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=test_cases_export.xlsx"}
        )

    except Exception as e:
        return Fail(msg=f"导出数据失败: {str(e)}")


@router.post("/generate", summary="AI生成测试用例")
@log_user_action(action="AI生成", resource_type="测试用例管理", description="AI生成测试用例")
async def generate_test_cases(
    api_endpoint_id: int = Body(..., description="API端点ID"),
    model_id: int = Body(..., description="AI模型ID"),
    generation_type: str = Body("comprehensive", description="生成类型"),
    test_count: int = Body(10, description="生成数量"),
    priority_distribution: Dict[str, int] = Body(..., description="优先级分布"),
    include_types: List[str] = Body(..., description="包含的测试类型"),
    description: Optional[str] = Body(None, description="备注说明"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """使用AI生成测试用例"""
    try:
        test_case_service = TestCaseService(db)

        # 验证优先级分布总和是否为100
        total_priority = sum(priority_distribution.values())
        if total_priority != 100:
            return Fail(msg="优先级分布总和必须为100%")

        # 生成测试用例
        generation_result = await test_case_service.generate_test_cases_by_ai(
            api_endpoint_id=api_endpoint_id,
            model_id=model_id,
            generation_type=generation_type,
            test_count=test_count,
            priority_distribution=priority_distribution,
            include_types=include_types,
            description=description,
            generated_by=current_user.id
        )

        return Success(data=generation_result, msg="AI生成测试用例成功")

    except Exception as e:
        return Fail(msg=f"AI生成测试用例失败: {str(e)}")


@router.get("/generation/history", summary="获取生成历史")
@log_user_action(action="查看", resource_type="测试用例管理", description="查看生成历史")
async def get_generation_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AI生成测试用例的历史记录"""
    try:
        test_case_service = TestCaseService(db)

        # 获取生成历史
        history, total = await test_case_service.get_generation_history(
            page=page,
            page_size=page_size,
            user_id=current_user.id
        )

        # 构建响应数据
        history_list = []
        for record in history:
            history_data = {
                "id": record.id,
                "api_endpoint": record.api_endpoint_info if hasattr(record, 'api_endpoint_info') else "",
                "generation_type": record.generation_type,
                "generated_count": record.generated_count,
                "success_count": record.success_count,
                "status": record.status,
                "created_at": record.create_time.strftime("%Y-%m-%d %H:%M:%S") if record.create_time else ""
            }
            history_list.append(history_data)

        response_data = {
            "items": history_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取生成历史失败: {str(e)}")


@router.post("/search", summary="搜索测试用例")
@log_user_action(action="搜索", resource_type="测试用例管理", description="搜索测试用例")
async def search_test_cases(
    keyword: Optional[str] = Body(None, description="关键词"),
    module: Optional[str] = Body(None, description="所属模块"),
    priority: Optional[str] = Body(None, description="优先级"),
    test_type: Optional[str] = Body(None, description="测试类型"),
    status: Optional[str] = Body(None, description="状态"),
    page: int = Body(1, description="页码"),
    page_size: int = Body(20, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索测试用例"""
    try:
        test_case_service = TestCaseService(db)

        # 构建搜索条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if module:
            filters['module'] = module
        if priority:
            filters['priority'] = priority
        if test_type:
            filters['test_type'] = test_type
        if status:
            filters['status'] = status

        # 执行搜索
        test_cases, total = await test_case_service.search_test_cases(
            filters=filters,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        test_case_list = []
        for test_case in test_cases:
            test_case_data = {
                "id": test_case.id,
                "name": test_case.name,
                "module": test_case.module,
                "description": test_case.description or "",
                "preconditions": test_case.preconditions or "",
                "test_steps": test_case.test_steps or "",
                "expected_result": test_case.expected_result or "",
                "priority": test_case.priority,
                "test_type": test_case.test_type,
                "status": test_case.status,
                "created_at": test_case.create_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.create_time else "",
                "updated_at": test_case.update_time.strftime("%Y-%m-%d %H:%M:%S") if test_case.update_time else ""
            }
            test_case_list.append(test_case_data)

        response_data = {
            "items": test_case_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"搜索测试用例失败: {str(e)}")


@router.get("/statistics/overview", summary="获取测试用例统计概览")
@log_user_action(action="查看", resource_type="测试用例管理", description="查看用例统计")
async def get_test_case_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试用例统计概览"""
    try:
        test_case_service = TestCaseService(db)
        
        # 获取统计数据
        statistics = await test_case_service.get_test_case_statistics()
        
        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取统计数据失败: {str(e)}")
