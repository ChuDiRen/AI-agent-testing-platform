"""
菜单管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.menu import Menu
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func
from app.services.menu import menu as menu_crud

router = APIRouter(prefix="/menu", tags=["菜单管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有菜单（树形结构）"""
    try:
        menus = await menu_crud.get_tree(db, parent_id=0)
        return respModel().ok_resp_tree(treeData=menus, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    pageSize: int = Query(10, ge=1, le=100, description='每页数量'),
    title: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询菜单（列表形式）"""
    try:
        query = select(Menu)
        
        # 添加筛选条件
        if title:
            query = query.where(Menu.title.like(f"%{title}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        skip = (page - 1) * pageSize
        query = query.offset(skip).limit(pageSize).order_by(Menu.order.asc())
        result = await db.execute(query)
        items = result.scalars().all()
        
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='菜单ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询菜单"""
    try:
        result = await db.execute(select(Menu).where(Menu.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("菜单不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/tree", response_model=respModel)
async def get_tree(
    *,
    parentId: int = Query(0, description='父菜单ID'),
    isHidden: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取菜单树"""
    try:
        menus = await menu_crud.get_tree(db, parent_id=parentId, is_hidden=isHidden)
        return respModel().ok_resp_tree(treeData=menus, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryTree", response_model=respModel)
async def query_tree(
    *,
    parentId: int = Query(0, description='父菜单ID'),
    isHidden: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """查询菜单树（前端调用别名）"""
    return await get_tree(parentId=parentId, isHidden=isHidden, db=db)


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    menu_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建菜单"""
    try:
        # 创建新菜单
        menu = Menu(
            title=menu_data.get('title'),
            path=menu_data.get('path'),
            component=menu_data.get('component'),
            icon=menu_data.get('icon'),
            parent_id=menu_data.get('parent_id', 0),
            order=menu_data.get('order', 0),
            is_hidden=menu_data.get('is_hidden', False),
            keepalive=menu_data.get('keepalive', True),
            meta=menu_data.get('meta')
        )
        
        db.add(menu)
        await db.flush()  # 获取ID
        await db.commit()
        
        return respModel().ok_resp(dic_t={"id": menu.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    menu_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新菜单"""
    try:
        menu_id = menu_data.get('id')
        result = await db.execute(select(Menu).where(Menu.id == menu_id))
        menu = result.scalars().first()
        if not menu:
            raise NotFoundException("菜单不存在")
        
        # 更新字段
        if 'title' in menu_data:
            menu.title = menu_data['title']
        if 'path' in menu_data:
            menu.path = menu_data['path']
        if 'component' in menu_data:
            menu.component = menu_data['component']
        if 'icon' in menu_data:
            menu.icon = menu_data['icon']
        if 'parent_id' in menu_data:
            menu.parent_id = menu_data['parent_id']
        if 'order' in menu_data:
            menu.order = menu_data['order']
        if 'is_hidden' in menu_data:
            menu.is_hidden = menu_data['is_hidden']
        if 'keepalive' in menu_data:
            menu.keepalive = menu_data['keepalive']
        if 'meta' in menu_data:
            menu.meta = menu_data['meta']
        
        await db.commit()
        return respModel().ok_resp(msg="修改成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=respModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='菜单ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除菜单"""
    try:
        result = await db.execute(select(Menu).where(Menu.id == id))
        menu = result.scalars().first()
        if not menu:
            raise NotFoundException("菜单不存在")
        
        # 检查是否有子菜单
        has_children = await menu_crud.has_children(db, id)
        if has_children:
            raise BadRequestException("该菜单下还有子菜单，不能删除")
        
        await db.delete(menu)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
