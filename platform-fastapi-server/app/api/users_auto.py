# 用户管理API - 自动生成示例

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_session
from .models import User
from .schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """创建用户"""
    db_user = User(**user.dict())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """获取用户列表"""
    users = session.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """获取用户详情"""
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    """更新用户"""
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    """删除用户"""
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    session.delete(user)
    session.commit()
    return {"message": "用户删除成功"}
