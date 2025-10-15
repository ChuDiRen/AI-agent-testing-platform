"""
AI模型配置模块API
提供AI模型的CRUD、批量操作和导出功能
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
from app.service.ai_model_service import AIModelService
from app.utils.log_decorators import log_user_action

router = APIRouter()


@router.get("/", summary="获取AI模型列表")
@log_user_action(action="查看", resource_type="AI模型配置", description="查看模型列表")
async def get_model_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="模型名称关键词"),
    provider: Optional[str] = Query(None, description="提供商"),
    model_type: Optional[str] = Query(None, description="模型类型"),
    status: Optional[str] = Query(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AI模型列表（分页）"""
    try:
        model_service = AIModelService(db)

        # 构建查询条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if provider:
            filters['provider'] = provider
        if model_type:
            filters['model_type'] = model_type
        if status:
            filters['status'] = status

        # 获取模型列表
        models, total = await model_service.get_model_list(
            page=page,
            page_size=page_size,
            filters=filters
        )

        # 构建响应数据
        model_list = []
        for model in models:
            model_data = {
                "id": model.id,
                "name": model.name,
                "display_name": model.display_name or model.name,
                "provider": model.provider,
                "model_type": model.model_type,
                "version": model.version or "",
                "status": model.status,
                "api_key": model.api_key[:10] + "***" if model.api_key else "",  # 脱敏显示
                "base_url": model.base_url or "",
                "temperature": model.temperature if hasattr(model, 'temperature') else 0.7,
                "description": model.description or "",
                "created_at": model.create_time.strftime("%Y-%m-%d %H:%M:%S") if model.create_time else "",
                "updated_at": model.update_time.strftime("%Y-%m-%d %H:%M:%S") if model.update_time else ""
            }
            model_list.append(model_data)

        response_data = {
            "items": model_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取模型列表失败: {str(e)}")


@router.get("/{model_id}", summary="获取单个模型详情")
@log_user_action(action="查看", resource_type="AI模型配置", description="查看模型详情")
async def get_model_detail(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个AI模型的详细信息"""
    try:
        model_service = AIModelService(db)
        model = await model_service.get_model_by_id(model_id)

        if not model:
            return Fail(msg="模型不存在")

        model_data = {
            "id": model.id,
            "name": model.name,
            "display_name": model.display_name or model.name,
            "provider": model.provider,
            "model_type": model.model_type,
            "version": model.version or "",
            "status": model.status,
            "api_key": model.api_key,  # 详情页显示完整信息
            "base_url": model.base_url or "",
            "temperature": model.temperature if hasattr(model, 'temperature') else 0.7,
            "description": model.description or "",
            "config": model.config or {},
            "created_at": model.create_time.strftime("%Y-%m-%d %H:%M:%S") if model.create_time else "",
            "updated_at": model.update_time.strftime("%Y-%m-%d %H:%M:%S") if model.update_time else ""
        }

        return Success(data=model_data)

    except Exception as e:
        return Fail(msg=f"获取模型详情失败: {str(e)}")


@router.post("/", summary="创建AI模型")
@log_user_action(action="新建", resource_type="AI模型配置", description="新建模型")
async def create_model(
    name: str = Body(..., description="模型名称"),
    display_name: Optional[str] = Body(None, description="显示名称"),
    provider: str = Body(..., description="提供商"),
    model_type: str = Body(..., description="模型类型"),
    version: Optional[str] = Body(None, description="版本"),
    api_key: str = Body(..., description="API密钥"),
    base_url: Optional[str] = Body(None, description="Base URL"),
    temperature: float = Body(0.7, description="温度参数"),
    description: Optional[str] = Body(None, description="描述"),
    config: Optional[Dict[str, Any]] = Body(default={}, description="额外配置"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的AI模型"""
    try:
        model_service = AIModelService(db)

        # 检查模型名称是否已存在
        existing_model = await model_service.get_model_by_name(name)
        if existing_model:
            return Fail(msg="模型名称已存在")

        # 创建模型
        new_model = await model_service.create_model(
            name=name,
            display_name=display_name or name,
            provider=provider,
            model_type=model_type,
            version=version,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            description=description,
            config=config,
            created_by=current_user.id
        )

        return Success(data={"id": new_model.id}, msg="创建成功")

    except Exception as e:
        return Fail(msg=f"创建模型失败: {str(e)}")


@router.put("/{model_id}", summary="更新AI模型")
@log_user_action(action="编辑", resource_type="AI模型配置", description="编辑模型")
async def update_model(
    model_id: int,
    name: Optional[str] = Body(None, description="模型名称"),
    display_name: Optional[str] = Body(None, description="显示名称"),
    provider: Optional[str] = Body(None, description="提供商"),
    model_type: Optional[str] = Body(None, description="模型类型"),
    version: Optional[str] = Body(None, description="版本"),
    api_key: Optional[str] = Body(None, description="API密钥"),
    base_url: Optional[str] = Body(None, description="Base URL"),
    temperature: Optional[float] = Body(None, description="温度参数"),
    description: Optional[str] = Body(None, description="描述"),
    config: Optional[Dict[str, Any]] = Body(None, description="额外配置"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新AI模型信息"""
    try:
        model_service = AIModelService(db)

        # 检查模型是否存在
        model = await model_service.get_model_by_id(model_id)
        if not model:
            return Fail(msg="模型不存在")

        # 检查名称冲突
        if name and name != model.name:
            existing_model = await model_service.get_model_by_name(name)
            if existing_model:
                return Fail(msg="模型名称已存在")

        # 更新模型
        await model_service.update_model(
            model_id=model_id,
            name=name,
            display_name=display_name,
            provider=provider,
            model_type=model_type,
            version=version,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            description=description,
            config=config,
            updated_by=current_user.id
        )

        return Success(msg="更新成功")

    except Exception as e:
        return Fail(msg=f"更新模型失败: {str(e)}")


@router.delete("/{model_id}", summary="删除AI模型")
@log_user_action(action="删除", resource_type="AI模型配置", description="删除模型")
async def delete_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除AI模型"""
    try:
        model_service = AIModelService(db)

        # 检查模型是否存在
        model = await model_service.get_model_by_id(model_id)
        if not model:
            return Fail(msg="模型不存在")

        # 检查是否有依赖
        dependencies = await model_service.check_model_dependencies(model_id)
        if dependencies:
            return Fail(msg=f"模型正在被使用，无法删除。依赖项：{', '.join(dependencies)}")

        # 删除模型
        await model_service.delete_model(model_id)

        return Success(msg="删除成功")

    except Exception as e:
        return Fail(msg=f"删除模型失败: {str(e)}")


@router.post("/{model_id}/test", summary="测试模型连接")
@log_user_action(action="测试连接", resource_type="AI模型配置", description="测试模型连接")
async def test_model_connection(
    model_id: int,
    test_message: str = Body("Hello", description="测试消息"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """测试AI模型连接"""
    try:
        model_service = AIModelService(db)

        # 检查模型是否存在
        model = await model_service.get_model_by_id(model_id)
        if not model:
            return Fail(msg="模型不存在")

        # 测试连接
        test_result = await model_service.test_model_connection(model_id, test_message)

        return Success(data=test_result, msg="连接测试完成")

    except Exception as e:
        return Fail(msg=f"连接测试失败: {str(e)}")


@router.post("/batch/update", summary="批量更新模型")
@log_user_action(action="批量更新", resource_type="AI模型配置", description="批量更新模型")
async def batch_update_models(
    model_ids: List[int] = Body(..., description="模型ID列表"),
    status: Optional[str] = Body(None, description="状态"),
    provider: Optional[str] = Body(None, description="提供商"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量更新AI模型"""
    try:
        model_service = AIModelService(db)

        if not model_ids:
            return Fail(msg="请选择要更新的模型")

        # 构建更新数据
        update_data = {}
        if status is not None:
            update_data['status'] = status
        if provider is not None:
            update_data['provider'] = provider

        if not update_data:
            return Fail(msg="请提供要更新的字段")

        # 执行批量更新
        success_count, error_messages = await model_service.batch_update_models(
            model_ids=model_ids,
            update_data=update_data,
            updated_by=current_user.id
        )

        if error_messages:
            return Success(
                data={"success_count": success_count, "errors": error_messages},
                msg=f"批量更新完成，成功 {success_count} 个，失败 {len(error_messages)} 个"
            )
        else:
            return Success(
                data={"success_count": success_count},
                msg=f"批量更新完成，成功更新 {success_count} 个模型"
            )

    except Exception as e:
        return Fail(msg=f"批量更新失败: {str(e)}")


@router.post("/batch/delete", summary="批量删除模型")
@log_user_action(action="批量删除", resource_type="AI模型配置", description="批量删除模型")
async def batch_delete_models(
    model_ids: List[int] = Body(..., description="模型ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量删除AI模型"""
    try:
        model_service = AIModelService(db)

        if not model_ids:
            return Fail(msg="请选择要删除的模型")

        # 执行批量删除
        success_count, error_messages = await model_service.batch_delete_models(
            model_ids=model_ids,
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
                msg=f"批量删除完成，成功删除 {success_count} 个模型"
            )

    except Exception as e:
        return Fail(msg=f"批量删除失败: {str(e)}")


@router.get("/export", summary="导出模型配置数据")
@log_user_action(action="导出", resource_type="AI模型配置", description="导出模型数据")
async def export_models(
    keyword: Optional[str] = Query(None, description="模型名称关键词"),
    provider: Optional[str] = Query(None, description="提供商"),
    model_type: Optional[str] = Query(None, description="模型类型"),
    status: Optional[str] = Query(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出AI模型配置数据为Excel文件"""
    try:
        model_service = AIModelService(db)

        # 构建查询条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if provider:
            filters['provider'] = provider
        if model_type:
            filters['model_type'] = model_type
        if status:
            filters['status'] = status

        # 获取所有符合条件的模型（不分页）
        models = await model_service.get_all_models(filters=filters)

        # 构建导出数据
        export_data = []
        for model in models:
            export_data.append({
                "ID": model.id,
                "模型名称": model.name,
                "显示名称": model.display_name or model.name,
                "提供商": model.provider,
                "模型类型": model.model_type,
                "版本": model.version or "",
                "状态": model.status,
                "API密钥": model.api_key[:10] + "***" if model.api_key else "",  # 导出时也要脱敏
                "Base URL": model.base_url or "",
                "温度参数": model.temperature if hasattr(model, 'temperature') else 0.7,
                "描述": model.description or "",
                "创建时间": model.create_time.strftime("%Y-%m-%d %H:%M:%S") if model.create_time else "",
                "更新时间": model.update_time.strftime("%Y-%m-%d %H:%M:%S") if model.update_time else ""
            })

        # 创建Excel文件
        df = pd.DataFrame(export_data)
        
        # 使用内存缓冲区
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='AI模型配置', index=False)
        
        output.seek(0)

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=ai_models_export.xlsx"}
        )

    except Exception as e:
        return Fail(msg=f"导出数据失败: {str(e)}")


@router.get("/providers", summary="获取模型提供商列表")
@log_user_action(action="查看", resource_type="AI模型配置", description="查看提供商列表")
async def get_model_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取支持的模型提供商列表"""
    try:
        model_service = AIModelService(db)
        providers = await model_service.get_supported_providers()
        
        return Success(data=providers)

    except Exception as e:
        return Fail(msg=f"获取提供商列表失败: {str(e)}")


@router.post("/search", summary="搜索AI模型")
@log_user_action(action="搜索", resource_type="AI模型配置", description="搜索模型")
async def search_models(
    keyword: Optional[str] = Body(None, description="关键词"),
    provider: Optional[str] = Body(None, description="提供商"),
    model_type: Optional[str] = Body(None, description="模型类型"),
    status: Optional[str] = Body(None, description="状态"),
    page: int = Body(1, description="页码"),
    page_size: int = Body(20, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索AI模型"""
    try:
        model_service = AIModelService(db)

        # 构建搜索条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if provider:
            filters['provider'] = provider
        if model_type:
            filters['model_type'] = model_type
        if status:
            filters['status'] = status

        # 执行搜索
        models, total = await model_service.search_models(
            filters=filters,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        model_list = []
        for model in models:
            model_data = {
                "id": model.id,
                "name": model.name,
                "display_name": model.display_name or model.name,
                "provider": model.provider,
                "model_type": model.model_type,
                "version": model.version or "",
                "status": model.status,
                "api_key": model.api_key[:10] + "***" if model.api_key else "",
                "base_url": model.base_url or "",
                "temperature": model.temperature if hasattr(model, 'temperature') else 0.7,
                "description": model.description or "",
                "created_at": model.create_time.strftime("%Y-%m-%d %H:%M:%S") if model.create_time else "",
                "updated_at": model.update_time.strftime("%Y-%m-%d %H:%M:%S") if model.update_time else ""
            }
            model_list.append(model_data)

        response_data = {
            "items": model_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"搜索模型失败: {str(e)}")


@router.get("/statistics", summary="获取模型统计信息")
@log_user_action(action="查看", resource_type="AI模型配置", description="查看模型统计")
async def get_model_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AI模型统计信息"""
    try:
        model_service = AIModelService(db)
        
        # 获取统计数据
        statistics = await model_service.get_model_statistics()
        
        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取统计数据失败: {str(e)}")


@router.post("/{model_id}/chat", summary="与模型对话")
@log_user_action(action="对话", resource_type="AI模型配置", description="与模型对话")
async def chat_with_model(
    model_id: int,
    message: str = Body(..., description="对话消息"),
    context: Optional[List[Dict[str, str]]] = Body(None, description="上下文"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """与AI模型进行对话"""
    try:
        model_service = AIModelService(db)

        # 检查模型是否存在
        model = await model_service.get_model_by_id(model_id)
        if not model:
            return Fail(msg="模型不存在")

        # 进行对话
        response = await model_service.chat_with_model(
            model_id=model_id,
            message=message,
            context=context,
            user_id=current_user.id
        )

        return Success(data=response, msg="对话成功")

    except Exception as e:
        return Fail(msg=f"对话失败: {str(e)}")


@router.post("/batch", summary="批量操作AI模型")
@log_user_action(action="批量操作", resource_type="AI模型配置", description="批量操作模型")
async def batch_operate_models(
    action: str = Body(..., description="操作类型: activate|deactivate|delete"),
    model_ids: List[int] = Body(..., description="模型ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量操作AI模型（兼容前端调用）"""
    try:
        model_service = AIModelService(db)

        if not model_ids:
            return Fail(msg="请选择要操作的模型")

        # 验证操作类型
        if action not in ["activate", "deactivate", "delete"]:
            return Fail(msg="不支持的操作类型")

        # 执行批量操作
        if action == "delete":
            success_count, error_messages = await model_service.batch_delete_models(
                model_ids=model_ids,
                deleted_by=current_user.id
            )
        else:
            # activate 或 deactivate 操作
            status = "active" if action == "activate" else "inactive"
            success_count, error_messages = await model_service.batch_update_models(
                model_ids=model_ids,
                update_data={"status": status},
                updated_by=current_user.id
            )

        if error_messages:
            return Success(
                data={"success_count": success_count, "errors": error_messages},
                msg=f"批量操作完成，成功 {success_count} 个，失败 {len(error_messages)} 个"
            )
        else:
            return Success(
                data={"success_count": success_count},
                msg=f"批量操作完成，成功操作 {success_count} 个模型"
            )

    except Exception as e:
        return Fail(msg=f"批量操作失败: {str(e)}")


@router.post("/{model_id}/status", summary="更新模型状态")
@log_user_action(action="状态变更", resource_type="AI模型配置", description="更新模型状态")
async def update_model_status(
    model_id: int,
    status: str = Body(..., description="新状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新模型状态"""
    try:
        model_service = AIModelService(db)

        # 检查模型是否存在
        model = await model_service.get_model_by_id(model_id)
        if not model:
            return Fail(msg="模型不存在")

        # 更新状态
        await model_service.update_model_status(model_id, status)

        return Success(msg="状态更新成功")

    except Exception as e:
        return Fail(msg=f"更新状态失败: {str(e)}")
