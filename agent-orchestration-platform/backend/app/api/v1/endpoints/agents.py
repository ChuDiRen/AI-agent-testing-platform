"""
Agent API 端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import agent_crud
from app.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.core.resp_model import RespModel


router = APIRouter(prefix="/Agent", tags=["Agent 管理"])


@router.post("/", response_model=RespModel)
async def create_agent(
    agent_in: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建 Agent"""
    # 安全验证：检查恶意输入
    malicious_patterns = [
        "<script>",
        "</script>",
        "javascript:",
        "data:",
        "vbscript:",
        "onload=",
        "onerror=",
        "onclick=",
        "DROP TABLE",
        "DELETE FROM",
        "INSERT INTO",
        "UPDATE SET",
        "SELECT *",
        "UNION SELECT",
        "' OR ",
        '" OR ',
        "1=1",
        "1 = 1",
        "../../",
        "..\\",
        "${jndi:",
        "$(",
        "`",
        "$(whoami)",
        "$(id)",
        "etc/passwd",
        "etc/shadow",
        "cmd.exe",
        "/bin/sh",
        "eval(",
        "exec(",
        "system("
    ]
    
    name_lower = agent_in.name.lower()
    desc_lower = (agent_in.description or "").lower()
    
    for pattern in malicious_patterns:
        if pattern.lower() in name_lower or pattern.lower() in desc_lower:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="输入包含不安全内容"
            )
    
    # 检查名称是否重复
    existing = await agent_crud.agent.get_by_name(db, name=agent_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent 名称 '{agent_in.name}' 已存在"
        )

    agent = await agent_crud.agent.create(db, obj_in=agent_in)
    # 转换为响应模型
    agent_response = AgentResponse.model_validate(agent)
    return RespModel.ok_resp(data=agent_response, msg="Agent 创建成功")


@router.get("/{agent_id}", response_model=RespModel)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取 Agent"""
    agent = await agent_crud.agent.get(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent ID {agent_id} 不存在"
        )
    # 转换为响应模型
    agent_response = AgentResponse.model_validate(agent)
    return RespModel.ok_resp(data=agent_response)


@router.get("/", response_model=RespModel)
async def list_agents(
    skip: int = 0,
    limit: int = 10,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取 Agent 列表"""
    if is_active is not None:
        agents = await agent_crud.agent.get_active_agents(db, skip=skip, limit=limit)
    else:
        agents = await agent_crud.agent.get_multi(db, skip=skip, limit=limit)

    total = await agent_crud.agent.count(db, filters={"is_active": is_active} if is_active else None)

    # 转换为响应模型列表
    agent_responses = [AgentResponse.model_validate(agent) for agent in agents]
    return RespModel.ok_resp_list(data=agent_responses, total=total)


@router.put("/{agent_id}", response_model=RespModel)
async def update_agent(
    agent_id: int,
    agent_in: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新 Agent"""
    db_agent = await agent_crud.agent.get(db, id=agent_id)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent ID {agent_id} 不存在"
        )

    agent = await agent_crud.agent.update(db, db_obj=db_agent, obj_in=agent_in)
    # 转换为响应模型
    agent_response = AgentResponse.model_validate(agent)
    return RespModel.ok_resp(data=agent_response, msg="Agent 更新成功")


@router.delete("/{agent_id}", response_model=RespModel)
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除 Agent"""
    db_agent = await agent_crud.agent.get(db, id=agent_id)
    if not db_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent ID {agent_id} 不存在"
        )

    await agent_crud.agent.remove(db, id=agent_id)
    return RespModel.ok_resp(msg="Agent 删除成功")
