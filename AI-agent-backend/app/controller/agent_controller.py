# Copyright (c) 2025 左岚. All rights reserved.
"""
AI代理Controller
处理AI代理相关的HTTP请求
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.service.agent_service import AgentService
from app.dto.agent_dto import (
    AgentCreateRequest, AgentUpdateRequest, AgentSearchRequest,
    AgentResponse, AgentListResponse, AgentStatisticsResponse,
    AgentStatusUpdateRequest, AgentBatchOperationRequest, AgentBatchOperationResponse
)
from app.dto.base import Success, Fail
from app.db.session import get_db
from app.middleware.auth import require_authentication
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["AI代理管理"])


@router.post("/", response_model=AgentResponse, summary="创建AI代理")
def create_agent(
    request: AgentCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """创建新的AI代理"""
    try:
        agent_service = AgentService(db)
        agent = agent_service.create_agent(request, current_user.get("user_id"))
        
        return Success(data=agent, msg="代理创建成功")
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        return Fail(msg=f"创建代理失败: {str(e)}")


@router.get("/{agent_id}", response_model=AgentResponse, summary="获取代理详情")
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """根据ID获取代理详情"""
    try:
        agent_service = AgentService(db)
        agent = agent_service.get_agent_by_id(agent_id)
        
        if not agent:
            return Fail(code=404, msg="代理不存在")
        
        return Success(data=agent)
        
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {str(e)}")
        return Fail(msg=f"获取代理失败: {str(e)}")


@router.put("/{agent_id}", response_model=AgentResponse, summary="更新代理信息")
def update_agent(
    agent_id: int,
    request: AgentUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """更新代理信息"""
    try:
        agent_service = AgentService(db)
        agent = agent_service.update_agent(agent_id, request)
        
        if not agent:
            return Fail(code=404, msg="代理不存在")
        
        return Success(data=agent, msg="代理更新成功")
        
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        return Fail(msg=f"更新代理失败: {str(e)}")


@router.delete("/{agent_id}", summary="删除代理")
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """删除代理"""
    try:
        agent_service = AgentService(db)
        success = agent_service.delete_agent(agent_id)
        
        if success:
            return Success(msg="代理删除成功")
        else:
            return Fail(msg="删除代理失败")
        
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        return Fail(msg=f"删除代理失败: {str(e)}")


@router.post("/search", response_model=AgentListResponse, summary="搜索代理")
def search_agents(
    request: AgentSearchRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """搜索代理列表"""
    try:
        agent_service = AgentService(db)
        result = agent_service.search_agents(request)
        
        return Success(data=result)
        
    except Exception as e:
        logger.error(f"Error searching agents: {str(e)}")
        return Fail(msg=f"搜索代理失败: {str(e)}")


@router.get("/", response_model=AgentListResponse, summary="获取代理列表")
def list_agents(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """获取代理列表"""
    try:
        request = AgentSearchRequest(page=page, page_size=page_size)
        agent_service = AgentService(db)
        result = agent_service.search_agents(request)
        
        return Success(data=result)
        
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return Fail(msg=f"获取代理列表失败: {str(e)}")


@router.get("/statistics/overview", response_model=AgentStatisticsResponse, summary="获取代理统计")
def get_agent_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """获取代理统计信息"""
    try:
        agent_service = AgentService(db)
        statistics = agent_service.get_agent_statistics()
        
        return Success(data=statistics)
        
    except Exception as e:
        logger.error(f"Error getting agent statistics: {str(e)}")
        return Fail(msg=f"获取统计信息失败: {str(e)}")


@router.post("/{agent_id}/start", response_model=AgentResponse, summary="启动代理")
def start_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """启动代理"""
    try:
        agent_service = AgentService(db)
        agent = agent_service.start_agent(agent_id)
        
        return Success(data=agent, msg="代理启动成功")
        
    except Exception as e:
        logger.error(f"Error starting agent {agent_id}: {str(e)}")
        return Fail(msg=f"启动代理失败: {str(e)}")


@router.post("/{agent_id}/stop", response_model=AgentResponse, summary="停止代理")
def stop_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """停止代理"""
    try:
        agent_service = AgentService(db)
        agent = agent_service.stop_agent(agent_id)
        
        return Success(data=agent, msg="代理停止成功")
        
    except Exception as e:
        logger.error(f"Error stopping agent {agent_id}: {str(e)}")
        return Fail(msg=f"停止代理失败: {str(e)}")


@router.post("/{agent_id}/status", response_model=AgentResponse, summary="更新代理状态")
def update_agent_status(
    agent_id: int,
    request: AgentStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """更新代理状态"""
    try:
        agent_service = AgentService(db)
        
        # 根据目标状态调用相应方法
        if request.status.value == "active":
            agent = agent_service._activate_agent(agent_id)
        elif request.status.value == "inactive":
            agent = agent_service._deactivate_agent(agent_id)
        elif request.status.value == "running":
            agent = agent_service.start_agent(agent_id)
        elif request.status.value == "stopped":
            agent = agent_service.stop_agent(agent_id)
        else:
            return Fail(msg=f"不支持的状态: {request.status.value}")
        
        # 获取更新后的代理信息
        updated_agent = agent_service.get_agent_by_id(agent_id)
        
        return Success(data=updated_agent, msg="代理状态更新成功")
        
    except Exception as e:
        logger.error(f"Error updating agent status {agent_id}: {str(e)}")
        return Fail(msg=f"更新代理状态失败: {str(e)}")


@router.post("/batch", response_model=AgentBatchOperationResponse, summary="批量操作代理")
def batch_operation_agents(
    request: AgentBatchOperationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_authentication)
):
    """批量操作代理"""
    try:
        agent_service = AgentService(db)
        result = agent_service.batch_operation(request)
        
        return Success(data=result, msg=f"批量操作完成: {result.success_count}/{result.total} 成功")
        
    except Exception as e:
        logger.error(f"Error in batch operation: {str(e)}")
        return Fail(msg=f"批量操作失败: {str(e)}")