"""
Execution 执行监控 API 端点（带 WebSocket）
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import execution_crud
from app.crud import agent_crud
from app.crud import workflow_crud
from app.schemas import ExecutionCreate
from app.core.resp_model import RespModel
from app.services.websocket_service import ws_manager
from app.services.execution_service import execution_engine


router = APIRouter(prefix="/Execution", tags=["Execution 监控"])


@router.websocket("/ws/{execution_id}")
async def execution_websocket(
    websocket: WebSocket,
    execution_id: int
):
    """WebSocket 连接点 - 实时监控执行状态"""
    await ws_manager.connect(websocket, execution_id)

    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()

            # 处理心跳包
            if data == "ping":
                await ws_manager.send_personal_message(
                    websocket,
                    {"type": "pong", "timestamp": "now"}
                )

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        await ws_manager.disconnect(websocket)


@router.post("/{execution_id}/start", response_model=RespModel)
async def start_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """开始执行 Workflow"""
    # 获取 execution 记录
    execution = await execution_crud.execution.get(db, id=execution_id)
    if not execution:
        return RespModel.error_resp(code=404, msg="Execution 不存在")

    # 获取 agent 和 workflow 配置
    agent = await agent_crud.agent.get(db, id=execution.agent_id)
    workflow = await workflow_crud.workflow.get(db, id=execution.workflow_id)

    if not agent or not workflow:
        return RespModel.error_resp(code=404, msg="Agent 或 Workflow 不存在")

    # 构建输入数据
    input_data = json.loads(execution.input_data) if execution.input_data else {}

    # 更新执行状态为 running
    from datetime import datetime
    execution = await execution_crud.execution.update(
        db, db_obj=execution, obj_in={"status": "running"}
    )

    # 异步执行工作流
    import asyncio
    asyncio.create_task(_run_workflow_streaming(execution_id, agent, workflow, input_data))

    return RespModel.ok_resp(data=execution, msg="Execution 已开始")


@router.post("/{execution_id}/pause", response_model=RespModel)
async def pause_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """暂停执行"""
    # TODO: 实现暂停逻辑
    await ws_manager.broadcast_to_execution(
        execution_id,
        {"type": "paused", "execution_id": execution_id}
    )
    return RespModel.ok_resp(msg="Execution 已暂停")


@router.post("/{execution_id}/resume", response_model=RespModel)
async def resume_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """恢复执行"""
    # TODO: 实现恢复逻辑
    await ws_manager.broadcast_to_execution(
        execution_id,
        {"type": "resumed", "execution_id": execution_id}
    )
    return RespModel.ok_resp(msg="Execution 已恢复")


async def _run_workflow_streaming(
    execution_id: int,
    agent: object,
    workflow: object,
    input_data: dict
):
    """异步执行工作流并流式推送状态"""
    try:
        # 构建图数据
        graph_data = json.loads(workflow.graph_data) if workflow.graph_data else {}

        # 构建配置
        agent_config = {
            "name": agent.name,
            "model": agent.model,
            "temperature": agent.temperature,
            "max_tokens": agent.max_tokens,
            "system_prompt": agent.system_prompt
        }

        # 执行工作流并流式推送
        async for event in execution_engine.execute_workflow(
            execution_id, graph_data, agent_config, input_data, execution_id
        ):
            await ws_manager.broadcast_to_execution(execution_id, event)

        # 记录使用量
        from app.models import Usage
        from datetime import datetime
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            usage = Usage(
                execution_id=execution_id,
                agent_id=agent.id,
                user_id=agent.created_by,
                tokens_used=1000,  # TODO: 从实际执行中获取
                execution_time=30,
                api_calls=1,
                cost=0.002  # TODO: 根据实际使用计算
            )
            session.add(usage)
            await session.commit()

    except Exception as e:
        # 推送错误消息
        await ws_manager.broadcast_to_execution(
            execution_id,
            {
                "type": "error",
                "execution_id": execution_id,
                "error": str(e)
            }
        )
