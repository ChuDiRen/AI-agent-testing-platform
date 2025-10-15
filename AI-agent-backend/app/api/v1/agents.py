"""
Agent模块API
提供AI代理的CRUD、批量操作和导出功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import pandas as pd

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.agent_service import AgentService
from app.utils.log_decorators import log_user_action

router = APIRouter()


@router.get("/", summary="获取AI代理列表")
@log_user_action(action="查看", resource_type="AI代理管理", description="查看代理列表")
async def get_agent_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="代理名称关键词"),
    type: Optional[str] = Query(None, description="代理类型"),
    status: Optional[str] = Query(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取AI代理列表（分页）"""
    try:
        agent_service = AgentService(db)

        # 构建查询条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if type:
            filters['type'] = type
        if status:
            filters['status'] = status

        # 获取代理列表
        agents, total = await agent_service.get_agent_list(
            page=page,
            page_size=page_size,
            filters=filters
        )

        # 构建响应数据
        agent_list = []
        for agent in agents:
            agent_data = {
                "id": agent.id,
                "name": agent.name,
                "type": agent.type,
                "status": agent.status,
                "version": agent.version,
                "description": agent.description or "",
                "config": agent.config or {},
                "created_at": agent.create_time.strftime("%Y-%m-%d %H:%M:%S") if agent.create_time else "",
                "updated_at": agent.update_time.strftime("%Y-%m-%d %H:%M:%S") if agent.update_time else ""
            }
            agent_list.append(agent_data)

        response_data = {
            "items": agent_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取代理列表失败: {str(e)}")


@router.get("/{agent_id}", summary="获取单个代理详情")
@log_user_action(action="查看", resource_type="AI代理管理", description="查看代理详情")
async def get_agent_detail(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个代理的详细信息"""
    try:
        agent_service = AgentService(db)
        agent = await agent_service.get_agent_by_id(agent_id)

        if not agent:
            return Fail(msg="代理不存在")

        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "status": agent.status,
            "version": agent.version,
            "description": agent.description or "",
            "config": agent.config or {},
            "created_at": agent.create_time.strftime("%Y-%m-%d %H:%M:%S") if agent.create_time else "",
            "updated_at": agent.update_time.strftime("%Y-%m-%d %H:%M:%S") if agent.update_time else ""
        }

        return Success(data=agent_data)

    except Exception as e:
        return Fail(msg=f"获取代理详情失败: {str(e)}")


@router.post("/", summary="创建AI代理")
@log_user_action(action="新建", resource_type="AI代理管理", description="新建代理")
async def create_agent(
    name: str = Body(..., description="代理名称"),
    type: str = Body(..., description="代理类型"),
    version: str = Body("1.0.0", description="版本号"),
    description: Optional[str] = Body(None, description="描述"),
    config: Optional[dict] = Body(default={}, description="配置信息"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的AI代理"""
    try:
        agent_service = AgentService(db)

        # 检查代理名称是否已存在
        existing_agent = await agent_service.get_agent_by_name(name)
        if existing_agent:
            return Fail(msg="代理名称已存在")

        # 创建代理
        new_agent = await agent_service.create_agent(
            name=name,
            type=type,
            version=version,
            description=description,
            config=config,
            created_by=current_user.id
        )

        return Success(data={"id": new_agent.id}, msg="创建成功")

    except Exception as e:
        return Fail(msg=f"创建代理失败: {str(e)}")


@router.put("/{agent_id}", summary="更新AI代理")
@log_user_action(action="编辑", resource_type="AI代理管理", description="编辑代理")
async def update_agent(
    agent_id: int,
    name: Optional[str] = Body(None, description="代理名称"),
    type: Optional[str] = Body(None, description="代理类型"),
    version: Optional[str] = Body(None, description="版本号"),
    description: Optional[str] = Body(None, description="描述"),
    config: Optional[dict] = Body(None, description="配置信息"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新AI代理信息"""
    try:
        agent_service = AgentService(db)

        # 检查代理是否存在
        agent = await agent_service.get_agent_by_id(agent_id)
        if not agent:
            return Fail(msg="代理不存在")

        # 检查名称冲突
        if name and name != agent.name:
            existing_agent = await agent_service.get_agent_by_name(name)
            if existing_agent:
                return Fail(msg="代理名称已存在")

        # 更新代理
        await agent_service.update_agent(
            agent_id=agent_id,
            name=name,
            type=type,
            version=version,
            description=description,
            config=config,
            updated_by=current_user.id
        )

        return Success(msg="更新成功")

    except Exception as e:
        return Fail(msg=f"更新代理失败: {str(e)}")


@router.delete("/{agent_id}", summary="删除AI代理")
@log_user_action(action="删除", resource_type="AI代理管理", description="删除代理")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除AI代理"""
    try:
        agent_service = AgentService(db)

        # 检查代理是否存在
        agent = await agent_service.get_agent_by_id(agent_id)
        if not agent:
            return Fail(msg="代理不存在")

        # 删除代理
        await agent_service.delete_agent(agent_id)

        return Success(msg="删除成功")

    except Exception as e:
        return Fail(msg=f"删除代理失败: {str(e)}")


@router.post("/{agent_id}/start", summary="启动AI代理")
@log_user_action(action="启动", resource_type="AI代理管理", description="启动代理")
async def start_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启动AI代理"""
    try:
        agent_service = AgentService(db)

        # 检查代理是否存在
        agent = await agent_service.get_agent_by_id(agent_id)
        if not agent:
            return Fail(msg="代理不存在")

        # 启动代理
        await agent_service.start_agent(agent_id)

        return Success(msg="代理启动成功")

    except Exception as e:
        return Fail(msg=f"启动代理失败: {str(e)}")


@router.post("/{agent_id}/stop", summary="停止AI代理")
@log_user_action(action="停止", resource_type="AI代理管理", description="停止代理")
async def stop_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """停止AI代理"""
    try:
        agent_service = AgentService(db)

        # 检查代理是否存在
        agent = await agent_service.get_agent_by_id(agent_id)
        if not agent:
            return Fail(msg="代理不存在")

        # 停止代理
        await agent_service.stop_agent(agent_id)

        return Success(msg="代理已停止")

    except Exception as e:
        return Fail(msg=f"停止代理失败: {str(e)}")


@router.post("/batch", summary="批量操作AI代理")
@log_user_action(action="批量操作", resource_type="AI代理管理", description="批量操作代理")
async def batch_operate_agents(
    action: str = Body(..., description="操作类型: start|stop|delete"),
    agent_ids: List[int] = Body(..., description="代理ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量操作AI代理"""
    try:
        agent_service = AgentService(db)

        if not agent_ids:
            return Fail(msg="请选择要操作的代理")

        # 验证操作类型
        if action not in ["start", "stop", "delete"]:
            return Fail(msg="不支持的操作类型")

        # 执行批量操作
        success_count, error_messages = await agent_service.batch_operate_agents(
            action=action,
            agent_ids=agent_ids,
            operator_id=current_user.id
        )

        if error_messages:
            return Success(
                data={"success_count": success_count, "errors": error_messages},
                msg=f"批量操作完成，成功 {success_count} 个，失败 {len(error_messages)} 个"
            )
        else:
            return Success(
                data={"success_count": success_count},
                msg=f"批量操作完成，成功操作 {success_count} 个代理"
            )

    except Exception as e:
        return Fail(msg=f"批量操作失败: {str(e)}")


@router.get("/export", summary="导出AI代理数据")
@log_user_action(action="导出", resource_type="AI代理管理", description="导出代理数据")
async def export_agents(
    keyword: Optional[str] = Query(None, description="代理名称关键词"),
    type: Optional[str] = Query(None, description="代理类型"),
    status: Optional[str] = Query(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出AI代理数据为Excel文件"""
    try:
        agent_service = AgentService(db)

        # 构建查询条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if type:
            filters['type'] = type
        if status:
            filters['status'] = status

        # 获取所有符合条件的代理（不分页）
        agents = await agent_service.get_all_agents(filters=filters)

        # 构建导出数据
        export_data = []
        for agent in agents:
            export_data.append({
                "ID": agent.id,
                "代理名称": agent.name,
                "代理类型": agent.type,
                "状态": agent.status,
                "版本": agent.version,
                "描述": agent.description or "",
                "创建时间": agent.create_time.strftime("%Y-%m-%d %H:%M:%S") if agent.create_time else "",
                "更新时间": agent.update_time.strftime("%Y-%m-%d %H:%M:%S") if agent.update_time else ""
            })

        # 创建Excel文件
        df = pd.DataFrame(export_data)
        
        # 使用内存缓冲区
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='AI代理列表', index=False)
        
        output.seek(0)

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=agents_export.xlsx"}
        )

    except Exception as e:
        return Fail(msg=f"导出数据失败: {str(e)}")


@router.get("/statistics/overview", summary="获取代理统计概览")
@log_user_action(action="查看", resource_type="AI代理管理", description="查看代理统计")
async def get_agent_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取代理统计概览"""
    try:
        agent_service = AgentService(db)
        
        # 获取统计数据
        statistics = await agent_service.get_agent_statistics()
        
        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取统计数据失败: {str(e)}")


@router.post("/search", summary="搜索AI代理")
@log_user_action(action="搜索", resource_type="AI代理管理", description="搜索代理")
async def search_agents(
    keyword: Optional[str] = Body(None, description="关键词"),
    type: Optional[str] = Body(None, description="代理类型"),
    status: Optional[str] = Body(None, description="状态"),
    page: int = Body(1, description="页码"),
    page_size: int = Body(20, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索AI代理"""
    try:
        agent_service = AgentService(db)

        # 构建搜索条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if type:
            filters['type'] = type
        if status:
            filters['status'] = status

        # 执行搜索
        agents, total = await agent_service.search_agents(
            filters=filters,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        agent_list = []
        for agent in agents:
            agent_data = {
                "id": agent.id,
                "name": agent.name,
                "type": agent.type,
                "status": agent.status,
                "version": agent.version,
                "description": agent.description or "",
                "config": agent.config or {},
                "created_at": agent.create_time.strftime("%Y-%m-%d %H:%M:%S") if agent.create_time else "",
                "updated_at": agent.update_time.strftime("%Y-%m-%d %H:%M:%S") if agent.update_time else ""
            }
            agent_list.append(agent_data)

        response_data = {
            "items": agent_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"搜索代理失败: {str(e)}")


@router.post("/{agent_id}/status", summary="更新代理状态")
@log_user_action(action="状态变更", resource_type="AI代理管理", description="更新代理状态")
async def update_agent_status(
    agent_id: int,
    status: str = Body(..., description="新状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新代理状态"""
    try:
        agent_service = AgentService(db)

        # 检查代理是否存在
        agent = await agent_service.get_agent_by_id(agent_id)
        if not agent:
            return Fail(msg="代理不存在")

        # 更新状态
        await agent_service.update_agent_status(agent_id, status)

        return Success(msg="状态更新成功")

    except Exception as e:
        return Fail(msg=f"更新状态失败: {str(e)}")
