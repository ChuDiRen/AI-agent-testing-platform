"""角色菜单关联管理 - 对应 t_role_menu 表"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.schemas.common import APIResponse
from app.schemas.menu import MenuResponse
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.role_menu import t_role_menu
from app.repositories.menu_repository import MenuRepository

router = APIRouter(prefix="/role-menus", tags=["角色菜单关联"])


class AssignMenusRequest(BaseModel):
    """分配菜单请求"""
    role_id: int
    menu_ids: List[int]


@router.post("/assign")
async def assign_menus_to_role(
    request: AssignMenusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """
    为角色分配菜单权限
    
    - **role_id**: 角色ID
    - **menu_ids**: 菜单ID列表
    """
    # 先删除现有关联
    await db.execute(
        t_role_menu.delete().where(t_role_menu.c.role_id == request.role_id)
    )
    
    # 添加新关联
    for menu_id in request.menu_ids:
        await db.execute(
            t_role_menu.insert().values(role_id=request.role_id, menu_id=menu_id)
        )
    
    await db.commit()
    
    return APIResponse(message="菜单权限分配成功")


@router.get("/{role_id}/menus", response_model=APIResponse[List[MenuResponse]])
async def get_role_menus(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[MenuResponse]]:
    """获取角色的菜单列表"""
    menu_repo = MenuRepository(db)
    menus = await menu_repo.get_menus_by_role_id(role_id)
    
    return APIResponse(
        data=[MenuResponse.model_validate(menu) for menu in menus]
    )


@router.delete("/{role_id}/menus/{menu_id}")
async def remove_menu_from_role(
    role_id: int,
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """移除角色的菜单权限"""
    result = await db.execute(
        t_role_menu.delete().where(
            (t_role_menu.c.role_id == role_id) & (t_role_menu.c.menu_id == menu_id)
        )
    )
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="关联不存在")
    
    return APIResponse(message="菜单权限移除成功")

