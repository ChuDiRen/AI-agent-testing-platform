# Copyright (c) 2025 左岚. All rights reserved.
"""
数据驱动测试API路由
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import io

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse

from ..services.ddt_service import DDTService
from ..models.ddt import ApiEngineDDT, ApiEngineDDTExecution
from ..schemas.case import CaseExecuteRequest

router = APIRouter()


@router.post("/", response_model=APIResponse[dict])
async def create_ddt(
    ddt_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建数据驱动测试数据集"""
    service = DDTService(db)

    try:
        ddt = await service.create_ddt(
            case_id=ddt_data["case_id"],
            name=ddt_data["name"],
            description=ddt_data.get("description", ""),
            data_source_type=ddt_data.get("data_source_type", "manual"),
            data_content=ddt_data.get("data_content"),
            file_path=ddt_data.get("file_path"),
            database_query=ddt_data.get("database_query"),
            database_config=ddt_data.get("database_config"),
            api_url=ddt_data.get("api_url"),
            api_headers=ddt_data.get("api_headers"),
            api_params=ddt_data.get("api_params"),
            execution_mode=ddt_data.get("execution_mode", "sequential"),
            max_parallel=ddt_data.get("max_parallel", 5),
            failure_strategy=ddt_data.get("failure_strategy", "continue"),
            max_retries=ddt_data.get("max_retries", 0),
            created_by=current_user.user_id
        )

        return APIResponse(
            success=True,
            message="数据集创建成功",
            data={"ddt_id": ddt.ddt_id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"创建失败: {str(e)}"
        )


@router.get("/", response_model=APIResponse[List[dict]])
async def get_ddts(
    case_id: int = Query(..., description="用例ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用例的数据驱动测试数据集列表"""
    service = DDTService(db)

    try:
        ddts = await service.get_ddts_by_case(case_id)
        return APIResponse(
            success=True,
            data=[
                {
                    "ddt_id": ddt.ddt_id,
                    "name": ddt.name,
                    "description": ddt.description,
                    "data_source_type": ddt.data_source_type,
                    "execution_mode": ddt.execution_mode,
                    "failure_strategy": ddt.failure_strategy,
                    "is_active": ddt.is_active,
                    "created_at": ddt.created_at.isoformat()
                }
                for ddt in ddts
            ]
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/{ddt_id}", response_model=APIResponse[dict])
async def get_ddt_detail(
    ddt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取数据集详情"""
    service = DDTService(db)

    try:
        ddt = await service.get_ddt(ddt_id)
        if not ddt:
            return APIResponse(
                success=False,
                message="数据集不存在"
            )

        # 获取测试数据
        test_data = await service.get_test_data(ddt)

        return APIResponse(
            success=True,
            data={
                "ddt_id": ddt.ddt_id,
                "case_id": ddt.case_id,
                "name": ddt.name,
                "description": ddt.description,
                "data_source_type": ddt.data_source_type,
                "data_content": ddt.data_content,
                "file_path": ddt.file_path,
                "file_type": ddt.file_type,
                "database_query": ddt.database_query,
                "database_config": ddt.database_config,
                "api_url": ddt.api_url,
                "api_headers": ddt.api_headers,
                "api_params": ddt.api_params,
                "execution_mode": ddt.execution_mode,
                "max_parallel": ddt.max_parallel,
                "failure_strategy": ddt.failure_strategy,
                "max_retries": ddt.max_retries,
                "is_active": ddt.is_active,
                "test_data": test_data,
                "test_data_count": len(test_data),
                "created_at": ddt.created_at.isoformat(),
                "updated_at": ddt.updated_at.isoformat()
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.put("/{ddt_id}", response_model=APIResponse[dict])
async def update_ddt(
    ddt_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新数据集"""
    service = DDTService(db)

    try:
        ddt = await service.update_ddt(ddt_id, update_data)
        if not ddt:
            return APIResponse(
                success=False,
                message="数据集不存在"
            )

        return APIResponse(
            success=True,
            message="更新成功",
            data={"ddt_id": ddt.ddt_id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"更新失败: {str(e)}"
        )


@router.delete("/{ddt_id}", response_model=APIResponse[dict])
async def delete_ddt(
    ddt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除数据集"""
    service = DDTService(db)

    try:
        success = await service.delete_ddt(ddt_id)
        if not success:
            return APIResponse(
                success=False,
                message="数据集不存在"
            )

        return APIResponse(
            success=True,
            message="删除成功"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"删除失败: {str(e)}"
        )


@router.post("/{ddt_id}/execute", response_model=APIResponse[dict])
async def execute_ddt(
    ddt_id: int,
    execute_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """执行数据驱动测试"""
    service = DDTService(db)

    try:
        result = await service.execute_ddt(
            ddt_id=ddt_id,
            execution_context=execute_data.get("context"),
            executed_by=current_user.user_id
        )

        return APIResponse(
            success=True,
            message="数据驱动测试执行已启动",
            data=result
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"执行失败: {str(e)}"
        )


@router.get("/batch/{batch_id}/results", response_model=APIResponse[List[dict]])
async def get_ddt_execution_results(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取DDT执行结果"""
    service = DDTService(db)

    try:
        executions = await service.get_ddt_execution_results(batch_id)
        return APIResponse(
            success=True,
            data=[
                {
                    "execution_id": exec.execution_id,
                    "data_index": exec.data_index,
                    "data_row": exec.data_row,
                    "status": exec.status,
                    "execution_result": exec.execution_result,
                    "error_message": exec.error_message,
                    "execution_time": exec.execution_time,
                    "started_at": exec.started_at.isoformat() if exec.started_at else None,
                    "finished_at": exec.finished_at.isoformat() if exec.finished_at else None
                }
                for exec in executions
            ]
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.get("/{ddt_id}/statistics", response_model=APIResponse[dict])
async def get_ddt_statistics(
    ddt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取DDT统计信息"""
    service = DDTService(db)

    try:
        stats = await service.get_ddt_statistics(ddt_id)
        return APIResponse(
            success=True,
            data=stats
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取失败: {str(e)}"
        )


@router.post("/import-file", response_model=APIResponse[dict])
async def import_ddt_from_file(
    case_id: int = Query(..., description="用例ID"),
    name: str = Query(..., description="数据集名称"),
    description: str = Query("", description="数据集描述"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """从文件导入数据驱动测试数据"""
    service = DDTService(db)

    try:
        # 保存上传的文件
        import os
        from datetime import datetime

        # 创建上传目录
        upload_dir = "uploads/ddt"
        os.makedirs(upload_dir, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"ddt_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)

        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 创建DDT数据集
        ddt = await service.import_data_from_file(
            case_id=case_id,
            file_path=file_path,
            name=name,
            description=description,
            created_by=current_user.user_id
        )

        return APIResponse(
            success=True,
            message="文件导入成功",
            data={
                "ddt_id": ddt.ddt_id,
                "file_path": file_path,
                "data_count": len(await service.get_test_data(ddt))
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"导入失败: {str(e)}"
        )


@router.get("/batch/{batch_id}/export/{format}")
async def export_ddt_results(
    batch_id: str,
    format: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """导出DDT执行结果"""
    service = DDTService(db)

    try:
        # 验证格式
        if format.lower() not in ['json', 'csv']:
            raise HTTPException(status_code=400, detail="不支持的导出格式")

        # 导出数据
        data = await service.export_ddt_results(batch_id, format)

        # 设置文件名和MIME类型
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if format.lower() == 'json':
            filename = f"ddt_results_{batch_id}_{timestamp}.json"
            media_type = "application/json"
        else:
            filename = f"ddt_results_{batch_id}_{timestamp}.csv"
            media_type = "text/csv"

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(data),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.post("/{ddt_id}/preview-data", response_model=APIResponse[dict])
async def preview_ddt_data(
    ddt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """预览DDT数据"""
    service = DDTService(db)

    try:
        ddt = await service.get_ddt(ddt_id)
        if not ddt:
            return APIResponse(
                success=False,
                message="数据集不存在"
            )

        test_data = await service.get_test_data(ddt)

        return APIResponse(
            success=True,
            data={
                "data_count": len(test_data),
                "sample_data": test_data[:5]  # 返回前5条数据作为预览
            }
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"预览失败: {str(e)}"
        )