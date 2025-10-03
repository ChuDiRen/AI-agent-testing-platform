"""菜单管理路由 - 对应 t_menu 表"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse, MenuTree
from app.schemas.common import APIResponse
from app.services.menu_service import MenuService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.post("/", response_model=APIResponse[MenuResponse], status_code=status.HTTP_201_CREATED)
async def create_menu(
    menu_data: MenuCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[MenuResponse]:
    """
    创建菜单/按钮
    
    - **parent_id**: 上级菜单ID，顶级菜单为0
    - **menu_name**: 菜单/按钮名称
    - **path**: 路由路径（菜单有效）
    - **component**: 组件路径（菜单有效）
    - **perms**: 权限标识，如 user:view, user:add
    - **icon**: 图标
    - **type**: 类型，0=菜单，1=按钮
    - **order_num**: 排序号
    """
    menu_service = MenuService(db)
    menu = await menu_service.create_menu(menu_data)
    
    return APIResponse(
        message="菜单创建成功",
        data=MenuResponse.model_validate(menu)
    )


@router.get("/", response_model=APIResponse[List[MenuResponse]])
async def get_menus(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[MenuResponse]]:
    """获取菜单列表"""
    menu_service = MenuService(db)
    menus = await menu_service.get_all_menus(skip=skip, limit=limit)
    
    return APIResponse(
        data=[MenuResponse.model_validate(menu) for menu in menus]
    )


@router.get("/tree", response_model=APIResponse[List[MenuTree]])
async def get_menu_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[MenuTree]]:
    """获取菜单树结构"""
    menu_service = MenuService(db)
    tree = await menu_service.get_menu_tree()
    
    return APIResponse(data=tree)


@router.get("/user/{user_id}", response_model=APIResponse[List[MenuResponse]])
async def get_user_menus(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[MenuResponse]]:
    """获取用户菜单（根据用户角色）"""
    menu_service = MenuService(db)
    menus = await menu_service.get_user_menus(user_id)
    
    return APIResponse(
        data=[MenuResponse.model_validate(menu) for menu in menus]
    )


@router.get("/{menu_id}", response_model=APIResponse[MenuResponse])
async def get_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[MenuResponse]:
    """获取菜单详情"""
    menu_service = MenuService(db)
    menu = await menu_service.get_menu_by_id(menu_id)
    
    return APIResponse(
        data=MenuResponse.model_validate(menu)
    )


@router.put("/{menu_id}", response_model=APIResponse[MenuResponse])
async def update_menu(
    menu_id: int,
    menu_data: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[MenuResponse]:
    """更新菜单"""
    menu_service = MenuService(db)
    menu = await menu_service.update_menu(menu_id, menu_data)
    
    return APIResponse(
        message="菜单更新成功",
        data=MenuResponse.model_validate(menu)
    )


@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除菜单"""
    menu_service = MenuService(db)
    await menu_service.delete_menu(menu_id)
    
    return APIResponse(message="菜单删除成功")

