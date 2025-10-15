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
        from app.dto.test_case_dto import TestCaseSearchRequest
        
        test_case_service = TestCaseService(db)

        # 使用 TestCaseSearchRequest 构建搜索请求
        search_request = TestCaseSearchRequest(
            keyword=keyword,
            module=module,
            priority=priority,
            test_type=test_type,
            status=status,
            page=page,
            page_size=page_size
        )

        # 调用 search_test_cases 方法（同步方法，不需要 await）
        result = test_case_service.search_test_cases(search_request)

        # 构建响应数据
        test_case_list = []
        for test_case_response in result.test_cases:
            test_case_data = {
                "id": test_case_response.id,
                "name": test_case_response.name,
                "module": test_case_response.module,
                "description": test_case_response.description or "",
                "preconditions": test_case_response.preconditions or "",
                "test_steps": test_case_response.test_steps or "",
                "expected_result": test_case_response.expected_result or "",
                "priority": test_case_response.priority,
                "test_type": test_case_response.test_type,
                "status": test_case_response.status,
                "created_at": test_case_response.created_at.strftime("%Y-%m-%d %H:%M:%S") if test_case_response.created_at else "",
                "updated_at": test_case_response.updated_at.strftime("%Y-%m-%d %H:%M:%S") if test_case_response.updated_at else ""
            }
            test_case_list.append(test_case_data)

        response_data = {
            "items": test_case_list,
            "total": result.total
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
        test_case = test_case_service.get_test_case_by_id(test_case_id)

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
        from app.dto.test_case_dto import TestCaseCreateRequest
        
        test_case_service = TestCaseService(db)

        # 创建测试用例
        request = TestCaseCreateRequest(
            name=name,
            module=module,
            description=description,
            preconditions=preconditions,
            test_steps=test_steps,
            expected_result=expected_result,
            priority=priority,
            test_type=test_type
        )
        new_test_case = test_case_service.create_test_case(request, current_user.id)

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
        from app.dto.test_case_dto import TestCaseUpdateRequest
        
        test_case_service = TestCaseService(db)

        # 检查测试用例是否存在
        test_case = test_case_service.get_test_case_by_id(test_case_id)
        if not test_case:
            return Fail(msg="测试用例不存在")

        # 更新测试用例
        request = TestCaseUpdateRequest(
            name=name,
            module=module,
            description=description,
            preconditions=preconditions,
            test_steps=test_steps,
            expected_result=expected_result,
            priority=priority,
            test_type=test_type
        )
        test_case_service.update_test_case(test_case_id, request)

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
        test_case = test_case_service.get_test_case_by_id(test_case_id)
        if not test_case:
            return Fail(msg="测试用例不存在")

        # 删除测试用例
        test_case_service.delete_test_case(test_case_id)

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
        test_case = test_case_service.get_test_case_by_id(test_case_id)
        if not test_case:
            return Fail(msg="测试用例不存在")

        # 执行测试用例
        execution_result = test_case_service.execute_test_case(test_case_id, current_user.id)

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

        # 简单实现：逐个执行
        success_count = 0
        error_messages = []
        results = []

        for test_case_id in test_case_ids:
            try:
                result = test_case_service.execute_test_case(test_case_id, current_user.id)
                results.append({"id": test_case_id, "result": result})
                success_count += 1
            except Exception as e:
                error_messages.append(f"测试用例 {test_case_id}: {str(e)}")

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
        from app.dto.test_case_dto import TestCaseBatchOperationRequest
        
        test_case_service = TestCaseService(db)

        if not test_case_ids:
            return Fail(msg="请选择要删除的测试用例")

        # 执行批量删除
        request = TestCaseBatchOperationRequest(
            test_case_ids=test_case_ids,
            operation='delete',
            operation_data={}
        )
        result = test_case_service.batch_operation(request)

        if result.errors:
            return Success(
                data={
                    "success_count": result.success_count,
                    "errors": result.errors,
                    "failed_ids": result.failed_ids
                },
                msg=f"批量删除完成，成功 {result.success_count} 个，失败 {result.failed_count} 个"
            )
        else:
            return Success(
                data={"success_count": result.success_count},
                msg=f"批量删除完成，成功删除 {result.success_count} 个测试用例"
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
        from app.dto.test_case_dto import TestCaseCreateRequest
        
        test_case_service = TestCaseService(db)

        if not test_cases:
            return Fail(msg="请提供要创建的测试用例数据")

        # 简单实现：逐个创建
        success_count = 0
        error_messages = []
        created_ids = []

        for tc_data in test_cases:
            try:
                request = TestCaseCreateRequest(
                    name=tc_data.get('name', ''),
                    module=tc_data.get('module', ''),
                    description=tc_data.get('description'),
                    preconditions=tc_data.get('preconditions'),
                    test_steps=tc_data.get('test_steps', ''),
                    expected_result=tc_data.get('expected_result', ''),
                    priority=tc_data.get('priority', 'P3'),
                    test_type=tc_data.get('test_type', 'functional')
                )
                result = test_case_service.create_test_case(request, current_user.id)
                created_ids.append(result.id)
                success_count += 1
            except Exception as e:
                error_messages.append(f"用例 {tc_data.get('name', '未命名')}: {str(e)}")

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
        from app.dto.test_case_dto import TestCaseSearchRequest
        
        test_case_service = TestCaseService(db)

        # 使用 search_test_cases 获取数据
        search_request = TestCaseSearchRequest(
            keyword=keyword,
            module=module,
            priority=priority,
            test_type=test_type,
            status=status,
            page=1,
            page_size=10000  # 设置一个大的值以获取所有数据
        )
        
        result = test_case_service.search_test_cases(search_request)
        test_cases = result.test_cases

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
                "创建时间": test_case.created_at.strftime("%Y-%m-%d %H:%M:%S") if test_case.created_at else "",
                "更新时间": test_case.updated_at.strftime("%Y-%m-%d %H:%M:%S") if test_case.updated_at else ""
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
        # 注意：AI生成功能需要集成AI服务，当前未实现
        return Fail(msg="AI生成测试用例功能正在开发中，敬请期待")

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
        from app.dto.test_case_dto import TestCaseGenerationHistoryRequest
        
        test_case_service = TestCaseService(db)

        # 获取生成历史
        request = TestCaseGenerationHistoryRequest(
            page=page,
            page_size=page_size,
            user_id=current_user.id
        )
        result = test_case_service.get_generation_history(request, current_user.id)

        # 构建响应数据
        history_list = []
        for record in result.history:
            history_data = {
                "id": record.id,
                "task_id": record.task_id,
                "requirement_summary": record.requirement_summary,
                "test_type": record.test_type,
                "priority": record.priority,
                "generated_count": record.generated_count,
                "status": record.status,
                "created_at": record.created_at if isinstance(record.created_at, str) else record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else ""
            }
            history_list.append(history_data)

        response_data = {
            "items": history_list,
            "total": result.total
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
        from app.dto.test_case_dto import TestCaseSearchRequest
        
        test_case_service = TestCaseService(db)

        # 使用 TestCaseSearchRequest 构建搜索请求
        search_request = TestCaseSearchRequest(
            keyword=keyword,
            module=module,
            priority=priority,
            test_type=test_type,
            status=status,
            page=page,
            page_size=page_size
        )

        # 执行搜索
        result = test_case_service.search_test_cases(search_request)

        # 构建响应数据
        test_case_list = []
        for test_case in result.test_cases:
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
                "created_at": test_case.created_at.strftime("%Y-%m-%d %H:%M:%S") if test_case.created_at else "",
                "updated_at": test_case.updated_at.strftime("%Y-%m-%d %H:%M:%S") if test_case.updated_at else ""
            }
            test_case_list.append(test_case_data)

        response_data = {
            "items": test_case_list,
            "total": result.total
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
        statistics = test_case_service.get_test_case_statistics()
        
        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取统计数据失败: {str(e)}")
