"""
机器人消息配置端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.robot_msg_config import RobotMsgConfig
from app.core.resp_model import RespModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func

router = APIRouter(prefix="/RobotMsgConfig", tags=["机器人消息配置"])


@router.get("/queryAll", response_model=ResponseModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有机器人消息配置"""
    try:
        result = await db.execute(select(RobotMsgConfig))
        items = result.scalars().all()
        return RespModel.success(data=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=ResponseModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    robot_id: Optional[int] = Query(None, description='机器人ID'),
    msg_type: Optional[str] = Query(None, description='消息类型'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询机器人消息配置"""
    try:
        query = select(RobotMsgConfig)
        
        # 添加筛选条件
        if robot_id:
            query = query.where(RobotMsgConfig.robot_id == robot_id)
        
        if msg_type:
            query = query.where(RobotMsgConfig.msg_type.like(f"%{msg_type}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return RespModel.success(data=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=ResponseModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='机器人消息配置ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询机器人消息配置"""
    try:
        result = await db.execute(select(RobotMsgConfig).where(RobotMsgConfig.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("机器人消息配置不存在")
        return RespModel.success(data=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=ResponseModel)
async def insert(
    *,
    msg_config_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建机器人消息配置"""
    try:
        msg_config = RobotMsgConfig(**msg_config_data)
        db.add(msg_config)
        await db.flush()
        await db.commit()
        return RespModel.success(data={"id": msg_config.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=ResponseModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='机器人消息配置ID'),
    msg_config_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新机器人消息配置"""
    try:
        result = await db.execute(select(RobotMsgConfig).where(RobotMsgConfig.id == id))
        msg_config = result.scalars().first()
        if not msg_config:
            raise NotFoundException("机器人消息配置不存在")
        
        # 更新字段
        for field, value in msg_config_data.items():
            if hasattr(msg_config, field):
                setattr(msg_config, field, value)
        
        await db.commit()
        return RespModel.success(msg="修改成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=ResponseModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='机器人消息配置ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除机器人消息配置"""
    try:
        result = await db.execute(select(RobotMsgConfig).where(RobotMsgConfig.id == id))
        msg_config = result.scalars().first()
        if not msg_config:
            raise NotFoundException("机器人消息配置不存在")
        
        await db.delete(msg_config)
        await db.commit()
        return RespModel.success(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
