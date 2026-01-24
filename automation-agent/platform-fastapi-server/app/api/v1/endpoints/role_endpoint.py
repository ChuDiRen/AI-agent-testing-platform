"""
角色管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleAssignMenus, RoleAssignApis
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func
from app.services.role import role as role_crud
from app.services.menu import menu as menu_crud
from app.services.api_resource import api_resource as api_crud
from app.models.role_menu import RoleMenu
from app.models.role_api import RoleApi

router = APIRouter(prefix="/role", tags=["角色管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有角色"""
    try:
        result = await db.execute(select(Role))
        items = result.scalars().all()
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    pageSize: int = Query(10, ge=1, le=100, description='每页数量'),
    name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询角色"""
    try:
        query = select(Role)
        
        # 添加筛选条件
        if name:
            query = query.where(Role.name.like(f"%{name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        skip = (page - 1) * pageSize
        query = query.offset(skip).limit(pageSize).order_by(Role.id.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='角色ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询角色"""
    try:
        result = await db.execute(select(Role).where(Role.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("角色不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    role_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建角色"""
    try:
        # 检查角色名是否已存在
        name = role_data.get('name')
        result = await db.execute(select(Role).where(Role.name == name))
        existing_role = result.scalars().first()
        if existing_role:
            raise BadRequestException("角色名已存在")
        
        # 创建新角色
        role = Role(
            name=name,
            desc=role_data.get('desc')
        )
        
        db.add(role)
        await db.flush()  # 获取ID
        await db.commit()
        
        return respModel().ok_resp(dic_t={"id": role.id}, msg="添加成功")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    role_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新角色"""
    try:
        role_id = role_data.get('id')
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        # 更新字段
        if 'name' in role_data:
            role.name = role_data['name']
        if 'desc' in role_data:
            role.desc = role_data['desc']
        
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
    id: int = Query(..., ge=1, description='角色ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除角色"""
    try:
        result = await db.execute(select(Role).where(Role.id == id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        await db.delete(role)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/queryMenus", response_model=respModel)
async def query_menus(
    *,
    id: int = Query(..., ge=1, description='角色ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询角色已分配的菜单"""
    try:
        # 查询角色已分配的菜单ID
        result = await db.execute(
            select(RoleMenu.menu_id).where(RoleMenu.role_id == id)
        )
        menu_ids = [row[0] for row in result.all()]
        
        # 查询所有菜单
        result = await db.execute(select(Role).where(Role.id == id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        # 获取菜单树
        menus = await menu_crud.get_tree(db, parent_id=0)
        
        # 标记已选中的菜单
        def mark_selected(menus_list):
            for menu in menus_list:
                menu.selected = menu.id in menu_ids
                if hasattr(menu, 'children') and menu.children:
                    mark_selected(menu.children)
            return menus_list
        
        marked_menus = mark_selected(menus)
        
        return respModel().ok_resp_simple_list(lst=marked_menus, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.put("/updateMenus", response_model=respModel)
async def update_menus(
    *,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新角色菜单分配"""
    try:
        role_id = data.get('id')
        menu_ids = data.get('menu_ids', [])
        
        # 验证角色存在
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        # 删除旧的菜单分配
        await db.execute(
            RoleMenu.__table__.delete().where(RoleMenu.role_id == role_id)
        )
        
        # 添加新的菜单分配
        if menu_ids:
            for menu_id in menu_ids:
                role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
                db.add(role_menu)
        
        await db.commit()
        return respModel().ok_resp(msg="分配成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"分配失败: {str(e)}")


@router.get("/queryApis", response_model=respModel)
async def query_apis(
    *,
    id: int = Query(..., ge=1, description='角色ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询角色已分配的API"""
    try:
        # 查询角色已分配的API ID
        result = await db.execute(
            select(RoleApi.api_id).where(RoleApi.role_id == id)
        )
        api_ids = [row[0] for row in result.all()]
        
        # 查询所有API
        result = await db.execute(select(Role).where(Role.id == id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        # 获取API列表
        result = await db.execute(select(api_crud.model))
        apis = result.scalars().all()
        
        # 标记已选中的API
        for api in apis:
            api.selected = api.id in api_ids
        
        return respModel().ok_resp_list(lst=apis, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.put("/updateApis", response_model=respModel)
async def update_apis(
    *,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新角色API分配"""
    try:
        role_id = data.get('id')
        api_ids = data.get('api_ids', [])
        
        # 验证角色存在
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        # 删除旧的API分配
        await db.execute(
            RoleApi.__table__.delete().where(RoleApi.role_id == role_id)
        )
        
        # 添加新的API分配
        if api_ids:
            for api_id in api_ids:
                role_api = RoleApi(role_id=role_id, api_id=api_id)
                db.add(role_api)
        
        await db.commit()
        return respModel().ok_resp(msg="分配成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"分配失败: {str(e)}")


@router.get("/authorized", response_model=respModel)
async def get_authorized(
    *,
    id: int = Query(..., ge=1, description='角色ID'),
    db: AsyncSession = Depends(get_db)
):
    """获取角色授权信息"""
    try:
        result = await db.execute(select(Role).where(Role.id == id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        # 获取已授权的菜单和API
        result = await db.execute(
            select(RoleMenu.menu_id).where(RoleMenu.role_id == id)
        )
        menu_ids = [row[0] for row in result.all()]
        
        result = await db.execute(
            select(RoleApi.api_id).where(RoleApi.role_id == id)
        )
        api_ids = [row[0] for row in result.all()]
        
        return respModel().ok_resp_simple(
            data={
                "role_id": role.id,
                "role_name": role.name,
                "menu_ids": menu_ids,
                "api_ids": api_ids
            },
            msg="查询成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/updateAuthorized", response_model=respModel)
async def update_authorized(
    *,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """批量更新角色授权（菜单和API）"""
    try:
        role_id = data.get('id')
        menu_ids = data.get('menu_ids', [])
        api_ids = data.get('api_ids', [])
        
        # 验证角色存在
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            raise NotFoundException("角色不存在")
        
        # 删除旧的菜单分配
        await db.execute(
            RoleMenu.__table__.delete().where(RoleMenu.role_id == role_id)
        )
        
        # 添加新的菜单分配
        if menu_ids:
            for menu_id in menu_ids:
                role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
                db.add(role_menu)
        
        # 删除旧的API分配
        await db.execute(
            RoleApi.__table__.delete().where(RoleApi.role_id == role_id)
        )
        
        # 添加新的API分配
        if api_ids:
            for api_id in api_ids:
                role_api = RoleApi(role_id=role_id, api_id=api_id)
                db.add(role_api)
        
        await db.commit()
        return respModel().ok_resp(msg="授权更新成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"授权更新失败: {str(e)}")
