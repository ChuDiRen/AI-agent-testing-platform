"""
Dept模块API - 完全按照vue-fastapi-admin标准实现
提供部门管理的CRUD功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.department_service import DepartmentService

router = APIRouter()


@router.get("/list", summary="获取部门列表")
async def get_dept_list(
    dept_name: Optional[str] = Query(None, description="部门名称"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取部门列表（树形结构）
    
    完全按照vue-fastapi-admin的接口规范实现
    返回完整的部门树，不分页
    """
    try:
        dept_service = DepartmentService(db)
        
        # 获取部门树
        dept_tree = dept_service.get_department_tree(keyword=dept_name)
        
        # 按照vue-fastapi-admin的响应格式
        return Success(data=dept_tree)
        
    except Exception as e:
        return Fail(msg=f"获取部门列表失败: {str(e)}")


@router.post("/create", summary="创建部门")
async def create_dept(
    parent_id: int = Body(0, description="父部门ID，0表示顶级部门"),
    dept_name: str = Body(..., description="部门名称"),
    order_num: Optional[float] = Body(0, description="排序号"),
    leader: Optional[str] = Body(None, description="负责人"),
    phone: Optional[str] = Body(None, description="联系电话"),
    email: Optional[str] = Body(None, description="邮箱"),
    status: str = Body("1", description="状态：0禁用 1启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新部门
    
    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        dept_service = DepartmentService(db)
        
        # 创建部门
        new_dept = dept_service.create_department(
            parent_id=parent_id,
            dept_name=dept_name,
            order_num=order_num,
            leader=leader,
            phone=phone,
            email=email,
            status=status
        )
        
        return Success(data={"dept_id": new_dept.id}, msg="创建成功")
        
    except ValueError as e:
        return Fail(msg=str(e))
    except Exception as e:
        return Fail(msg=f"创建部门失败: {str(e)}")


@router.post("/update", summary="更新部门")
async def update_dept(
    dept_id: int = Body(..., description="部门ID"),
    parent_id: int = Body(0, description="父部门ID"),
    dept_name: str = Body(..., description="部门名称"),
    order_num: Optional[float] = Body(0, description="排序号"),
    leader: Optional[str] = Body(None, description="负责人"),
    phone: Optional[str] = Body(None, description="联系电话"),
    email: Optional[str] = Body(None, description="邮箱"),
    status: str = Body("1", description="状态：0禁用 1启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新部门信息
    
    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        dept_service = DepartmentService(db)
        
        # 检查部门是否存在
        dept = dept_service.get_department_by_id(dept_id)
        if not dept:
            return Fail(msg="部门不存在")
        
        # 检查是否设置自己为父部门
        if parent_id == dept_id:
            return Fail(msg="不能设置自己为父部门")
        
        # 更新部门
        dept.parent_id = parent_id
        dept.dept_name = dept_name
        dept.order_num = order_num
        dept.leader = leader
        dept.phone = phone
        dept.email = email
        dept.status = status
        
        dept_service.db.commit()
        
        return Success(msg="更新成功")
        
    except Exception as e:
        dept_service.db.rollback()
        return Fail(msg=f"更新部门失败: {str(e)}")


@router.delete("/delete", summary="删除部门")
async def delete_dept(
    dept_id: int = Query(..., description="部门ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除部门
    
    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        dept_service = DepartmentService(db)
        
        # 检查部门是否存在
        dept = dept_service.get_department_by_id(dept_id)
        if not dept:
            return Fail(msg="部门不存在")
        
        # 检查是否有子部门
        children = dept_service.get_children_departments(dept_id)
        if children:
            return Fail(msg=f"该部门下有 {len(children)} 个子部门，请先删除子部门")
        
        # 检查是否有用户
        user_count = await dept_service.get_department_user_count(dept_id)
        if user_count > 0:
            return Fail(msg=f"该部门下有 {user_count} 个用户，请先移除用户")
        
        # 删除部门
        dept_service.delete_department(dept_id)
        
        return Success(msg="删除成功")
        
    except Exception as e:
        return Fail(msg=f"删除部门失败: {str(e)}")

