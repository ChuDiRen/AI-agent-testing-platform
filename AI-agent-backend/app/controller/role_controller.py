"""
角色Controller
处理角色相关的HTTP请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse, Success, Fail, SuccessExtra
from app.dto.role_dto import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleResponse,
    RoleListResponse,
    RoleMenuAssignRequest,
    RolePermissionResponse,
    RoleIdRequest,
    RoleListRequest,
    RoleDeleteRequest,
    RoleCopyRequest,
    RoleBatchDeleteRequest
)
from app.service.role_service import RoleService
from app.utils.log_decorators import log_operation, log_user_action
from app.middleware.auth import get_current_user
from app.entity.user import User

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("/create-role", response_model=ApiResponse[dict], summary="创建角色")
@log_operation(
    operation_type="CREATE",
    resource_type="ROLE",
    operation_desc="创建角色",
    include_request=True
)
async def create_role(
    request: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新角色
    
    - **role_name**: 角色名称（必填，最大10个字符）
    - **remark**: 角色描述（可选，最大100个字符）
    """
    try:
        role_service = RoleService(db)
        role = role_service.create_role(
            role_name=request.role_name,
            remark=request.remark
        )
        
        # 转换为字典格式
        role_dict = {
            "role_id": role.id,
            "role_name": role.role_name,
            "remark": role.remark,
            "create_time": role.create_time.isoformat() if role.create_time else None,
            "modify_time": role.modify_time.isoformat() if role.modify_time else None
        }

        logger.info(f"Role created successfully: {role.role_name}")
        return Success(code=200, msg="角色创建成功", data=role_dict)
        
    except ValueError as e:
        logger.warning(f"Role creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建角色失败"
        )


@router.post("/get-role-list", response_model=ApiResponse[list], summary="获取角色列表")
async def get_role_list(
    request: RoleListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色列表（支持分页和搜索）

    - **page**: 页码（从1开始）
    - **size**: 每页大小（1-100）
    - **keyword**: 关键词搜索
    """
    try:
        role_service = RoleService(db)
        result = role_service.get_roles_with_pagination(page=request.page, size=request.size, keyword=request.keyword)
        
        # 转换为字典格式
        roles = [
            {
                "role_id": role_data["role_id"],
                "role_name": role_data["role_name"],
                "remark": role_data["remark"],
                "create_time": role_data["create_time"].isoformat() if hasattr(role_data["create_time"], 'isoformat') and role_data["create_time"] else role_data["create_time"],
                "modify_time": role_data["modify_time"].isoformat() if hasattr(role_data["modify_time"], 'isoformat') and role_data["modify_time"] else role_data["modify_time"]
            }
            for role_data in result["roles"]
        ]

        return SuccessExtra(
            code=200,
            msg="获取角色列表成功",
            data=result["roles"],
            total=result["total"],
            page=request.page,
            size=request.size
        )
        
    except Exception as e:
        logger.error(f"Error getting role list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色列表失败"
        )


@router.post("/get-role-info", response_model=ApiResponse[dict], summary="获取角色详情")
async def get_role_info(
    request: RoleIdRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色详情
    
    - **role_id**: 角色ID（必填）
    """
    try:
        role_service = RoleService(db)
        role = role_service.get_role_by_id(request.role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 转换为字典格式
        role_dict = {
            "role_id": role.id,
            "role_name": role.role_name,
            "remark": role.remark,
            "create_time": role.create_time.isoformat() if role.create_time else None,
            "modify_time": role.modify_time.isoformat() if role.modify_time else None
        }

        return Success(code=200, msg="获取角色详情成功", data=role_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色详情失败"
        )


@router.post("/update-role", response_model=ApiResponse[dict], summary="更新角色")
@log_operation(
    operation_type="UPDATE",
    resource_type="ROLE",
    operation_desc="更新角色",
    include_request=True
)
async def update_role(
    request: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新角色信息
    
    - **role_id**: 角色ID（必填）
    - **role_name**: 角色名称（可选）
    - **remark**: 角色描述（可选）
    """
    try:
        role_service = RoleService(db)
        role = role_service.update_role(
            role_id=request.role_id,
            role_name=request.role_name,
            remark=request.remark
        )
        
        # 转换为字典格式
        role_dict = {
            "role_id": role.id,
            "role_name": role.role_name,
            "remark": role.remark,
            "create_time": role.create_time.isoformat() if role.create_time else None,
            "modify_time": role.modify_time.isoformat() if role.modify_time else None
        }

        logger.info(f"Role updated successfully: {role.role_name}")
        return Success(code=200, msg="角色更新成功", data=role_dict)
        
    except ValueError as e:
        logger.warning(f"Role update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error updating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败"
        )


@router.post("/delete-role", response_model=ApiResponse[bool], summary="删除角色")
@log_operation(
    operation_type="DELETE",
    resource_type="ROLE",
    operation_desc="删除角色",
    include_request=True
)
async def delete_role(
    request: RoleDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除角色
    
    - **role_id**: 角色ID（必填）
    """
    try:
        role_service = RoleService(db)
        
        # 检查角色是否存在
        role = role_service.get_role_by_id(request.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 检查角色是否被用户使用
        if role_service.is_role_in_use(request.role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色正在被用户使用，无法删除"
            )
        
        # 删除角色
        success = role_service.delete_role(request.role_id)
        
        if success:
            logger.info(f"Role deleted successfully: {role.role_name}")
            return Success(code=200, msg="角色删除成功", data=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除角色失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )


@router.post("/batch-delete", response_model=ApiResponse[dict], summary="批量删除角色")
@log_operation(
    operation_type="BATCH_DELETE",
    resource_type="ROLE",
    operation_desc="批量删除角色",
    include_request=True
)
async def batch_delete_roles(
    request: RoleBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量删除角色
    
    - **role_ids**: 角色ID列表（必填）
    """
    try:
        role_service = RoleService(db)
        
        success_count = 0
        failed_count = 0
        failed_roles = []
        
        for role_id in request.role_ids:
            try:
                # 检查角色是否存在
                role = role_service.get_role_by_id(role_id)
                if not role:
                    failed_count += 1
                    failed_roles.append({"role_id": role_id, "reason": "角色不存在"})
                    continue
                
                # 检查角色是否被用户使用
                if role_service.is_role_in_use(role_id):
                    failed_count += 1
                    failed_roles.append({"role_id": role_id, "reason": "角色正在被用户使用"})
                    continue
                
                # 删除角色
                if role_service.delete_role(role_id):
                    success_count += 1
                    logger.info(f"Role deleted successfully in batch: {role.role_name}")
                else:
                    failed_count += 1
                    failed_roles.append({"role_id": role_id, "reason": "删除失败"})
                    
            except Exception as e:
                failed_count += 1
                failed_roles.append({"role_id": role_id, "reason": str(e)})
        
        result = {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_roles": failed_roles
        }
        
        return Success(code=200, msg=f"批量删除完成，成功{success_count}个，失败{failed_count}个", data=result)
        
    except Exception as e:
        logger.error(f"Unexpected error in batch delete roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量删除角色失败"
        )


@router.post("/{role_id}/copy", response_model=ApiResponse[dict], summary="复制角色")
async def copy_role(
    role_id: int,
    request: RoleCopyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    复制角色
    
    - **role_id**: 源角色ID（必填）
    - **new_role_name**: 新角色名称（必填）
    - **remark**: 新角色描述（可选）
    """
    try:
        role_service = RoleService(db)
        
        # 检查源角色是否存在
        source_role = role_service.get_role_by_id(role_id)
        if not source_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="源角色不存在"
            )
        
        # 复制角色
        new_role = role_service.copy_role(
            source_role_id=role_id,
            new_role_name=request.new_role_name,
            remark=request.remark
        )
        
        # 转换为字典格式
        role_dict = {
            "role_id": new_role.id,
            "role_name": new_role.role_name,
            "remark": new_role.remark,
            "create_time": new_role.create_time.isoformat() if new_role.create_time else None,
            "modify_time": new_role.modify_time.isoformat() if new_role.modify_time else None
        }

        logger.info(f"Role copied successfully: {source_role.role_name} -> {new_role.role_name}")
        return Success(code=200, msg="角色复制成功", data=role_dict)
        
    except ValueError as e:
        logger.warning(f"Role copy failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error copying role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="复制角色失败"
        )


@router.post("/assign-role-menus", response_model=ApiResponse[bool], summary="分配菜单权限")
async def assign_role_menus(
    request: RoleMenuAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    为角色分配菜单权限

    - **role_id**: 角色ID（必填）
    - **menu_ids**: 菜单ID列表（必填）
    """
    try:
        role_service = RoleService(db)
        
        # 检查角色是否存在
        role = role_service.get_role_by_id(request.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 分配菜单权限
        success = role_service.assign_role_menus(request.role_id, request.menu_ids)
        
        if success:
            logger.info(f"Menus assigned to role successfully: {role.role_name}")
            return Success(code=200, msg="菜单权限分配成功", data=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="菜单权限分配失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error assigning role menus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配菜单权限失败"
        )


@router.post("/get-role-permissions", response_model=ApiResponse[dict], summary="获取角色权限")
async def get_role_permissions(
    request: RoleIdRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色的权限信息

    - **role_id**: 角色ID（必填）
    """
    try:
        role_service = RoleService(db)
        
        # 检查角色是否存在
        role = role_service.get_role_by_id(request.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 获取角色权限
        permissions = role_service.get_role_permissions(request.role_id)
        
        result = {
            "role_id": request.role_id,
            "role_name": role.role_name,
            "permissions": permissions
        }
        
        return Success(code=200, msg="获取角色权限成功", data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色权限失败"
        )
