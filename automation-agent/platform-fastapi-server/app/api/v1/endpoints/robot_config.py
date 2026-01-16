"""
机器人配置信息端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.crud.robot_config import robot_config_crud
from app.schemas.robot_config import RobotConfigCreate, RobotConfigUpdate, RobotConfigResponse
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/RobotConfig", tags=["机器人配置"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有机器人配置"""
    try:
        items = await robot_config_crud.get_multi(db)
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    robot_type: Optional[str] = Query(None, description='机器人类型'),
    robot_name: Optional[str] = Query(None, description='机器人名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询机器人配置"""
    try:
        items, total = await robot_config_crud.get_multi_with_filters(
            db, 
            page=page, 
            page_size=page_size,
            robot_type=robot_type,
            robot_name=robot_name
        )
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='机器人配置ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询机器人配置"""
    try:
        item = await robot_config_crud.get(db, id=id)
        if not item:
            raise NotFoundException("机器人配置不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    config_data: RobotConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建机器人配置"""
    try:
        item = await robot_config_crud.create(db, obj_in=config_data)
        return respModel().ok_resp(dic_t={"id": item.id}, msg="添加成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='机器人配置ID'),
    config_data: RobotConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新机器人配置"""
    try:
        item = await robot_config_crud.get(db, id=id)
        if not item:
            raise NotFoundException("机器人配置不存在")
        
        updated_item = await robot_config_crud.update(db, db_obj=item, obj_in=config_data)
        return respModel().ok_resp(msg="修改成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=respModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='机器人配置ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除机器人配置"""
    try:
        item = await robot_config_crud.get(db, id=id)
        if not item:
            raise NotFoundException("机器人配置不存在")
        
        await robot_config_crud.remove(db, id=id)
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/queryByPageWithFilter", response_model=respModel)
async def query_by_page_with_filter(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    coll_id: Optional[int] = Query(None, description='集合ID'),
    coll_type: Optional[str] = Query(None, description='集合类型'),
    robot_name: Optional[str] = Query(None, description='机器人名称'),
    type: Optional[int] = Query(None, description='机器人类型'),
    db: AsyncSession = Depends(get_db)
):
    """带过滤条件的分页查询机器人"""
    try:
        from app.models.robot_msg_config import RobotMsgConfig
        
        # 构建基础查询
        query = select(RobotConfig)
        
        # 添加类型过滤
        if type is not None:
            query = query.where(RobotConfig.robot_type == type)
        
        # 如果coll_id不为0，则查询已有的机器人ID列表并排除
        if coll_id and coll_id > 0:
            msg_config_result = await db.execute(
                select(RobotMsgConfig.robot_id).where(
                    RobotMsgConfig.coll_id == coll_id,
                    RobotMsgConfig.coll_type == coll_type
                )
            )
            existing_robot_ids = [row.robot_id for row in msg_config_result.scalars().all()]
            
            if existing_robot_ids:
                # 排除已有的机器人
                query = query.where(RobotConfig.id.notin_(existing_robot_ids))
        
        # 添加机器人名称模糊搜索
        if robot_name and len(robot_name) > 0:
            query = query.where(RobotConfig.robot_name.like(f"%{robot_name}%"))
        
        # 分页查询
        result = await db.execute(
            query.limit(page_size).offset((page - 1) * page_size)
        )
        datas = result.scalars().all()
        
        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return respModel().ok_resp_list(lst=datas, total=total, msg="查询成功")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
