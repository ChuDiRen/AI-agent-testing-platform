"""
用户管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有用户"""
    try:
        result = await db.execute(select(User))
        items = result.scalars().all()
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    username: Optional[str] = Query(None, description='用户名'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询用户"""
    try:
        query = select(User)
        
        # 添加筛选条件
        if username:
            query = query.where(User.username.like(f"%{username}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='用户ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询用户"""
    try:
        result = await db.execute(select(User).where(User.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("用户不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    try:
        # 检查用户名是否已存在
        result = await db.execute(select(User).where(User.username == user_data.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise BadRequestException("用户名已存在")
        
        # 创建新用户
        user = User(username=user_data.username)
        user.set_password(user_data.password)
        
        db.add(user)
        await db.flush()  # 获取ID
        await db.commit()
        
        return respModel().ok_resp(dic_t={"id": user.id}, msg="添加成功")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='用户ID'),
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新用户"""
    try:
        result = await db.execute(select(User).where(User.id == id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException("用户不存在")
        
        # 更新密码
        if user_data.password:
            user.set_password(user_data.password)
        
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
    id: int = Query(..., ge=1, description='用户ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    try:
        result = await db.execute(select(User).where(User.id == id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException("用户不存在")
        
        await db.delete(user)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/resetPassword", response_model=respModel)
async def reset_password(
    *,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """重置用户密码"""
    try:
        user_id = data.get('id')
        new_password = data.get('password', '123456')  # 默认密码
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException("用户不存在")
        
        # 重置密码
        user.set_password(new_password)
        await db.commit()
        
        return respModel().ok_resp(msg="密码重置成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"密码重置失败: {str(e)}")


@router.get("/profile", response_model=respModel)
async def get_profile(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """获取个人资料"""
    try:
        # 从请求头中获取 token
        token = request.headers.get("token")
        if not token:
            from app.core.exceptions import UnauthorizedException
            raise UnauthorizedException("未登录")
        
        # 验证 Token
        from app.core.security import verify_token
        payload = verify_token(token)
        if not payload:
            from app.core.exceptions import UnauthorizedException
            raise UnauthorizedException("Token 失效")
        
        # 从 token 中获取用户 ID
        user_id = payload.get("user_id") if isinstance(payload, dict) else payload.get("sub")
        
        # 查询用户
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException("用户不存在")
        
        # 构建返回数据
        profile_data = {
            "id": user.id,
            "username": user.username,
            "alias": user.alias,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "dept_id": user.dept_id,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
        return respModel().ok_resp(profile_data, msg="获取个人资料成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取个人资料失败: {str(e)}")


@router.put("/profile", response_model=respModel)
async def update_profile(
    request: Request,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新个人资料"""
    try:
        # 从请求头中获取 token
        token = request.headers.get("token")
        if not token:
            from app.core.exceptions import UnauthorizedException
            raise UnauthorizedException("未登录")
        
        # 验证 Token
        from app.core.security import verify_token
        payload = verify_token(token)
        if not payload:
            from app.core.exceptions import UnauthorizedException
            raise UnauthorizedException("Token 失效")
        
        # 从 token 中获取用户 ID
        user_id = payload.get("user_id") if isinstance(payload, dict) else payload.get("sub")
        
        # 查询用户
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException("用户不存在")
        
        # 更新允许修改的字段
        if 'alias' in data:
            user.alias = data['alias']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        
        await db.commit()
        
        return respModel().ok_resp(msg="个人资料更新成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"个人资料更新失败: {str(e)}")
