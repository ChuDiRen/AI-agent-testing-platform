"""
部门管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.dept import Dept
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func
from app.services.dept import dept as dept_crud

router = APIRouter(prefix="/dept", tags=["部门管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有部门（树形结构）"""
    try:
        depts = await dept_crud.get_tree(db, parent_id=0)
        return respModel().ok_resp_tree(treeData=depts, msg="查询成功")
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
    """分页查询部门（列表形式）"""
    try:
        query = select(Dept)
        
        # 添加筛选条件
        if name:
            query = query.where(Dept.name.like(f"%{name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        skip = (page - 1) * pageSize
        query = query.offset(skip).limit(pageSize).order_by(Dept.id.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='部门ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询部门"""
    try:
        result = await db.execute(select(Dept).where(Dept.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("部门不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/tree", response_model=respModel)
async def get_tree(
    *,
    parentId: int = Query(0, description='父部门ID'),
    db: AsyncSession = Depends(get_db)
):
    """获取部门树"""
    try:
        depts = await dept_crud.get_tree(db, parent_id=parentId)
        return respModel().ok_resp_tree(treeData=depts, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryTree", response_model=respModel)
async def query_tree(
    *,
    parentId: int = Query(0, description='父部门ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询部门树（前端调用别名）"""
    return await get_tree(parentId=parentId, db=db)


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    dept_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建部门"""
    try:
        # 创建新部门
        dept = Dept(
            name=dept_data.get('name'),
            parent_id=dept_data.get('parent_id', 0),
            leader=dept_data.get('leader'),
            phone=dept_data.get('phone'),
            email=dept_data.get('email'),
            address=dept_data.get('address'),
            order=dept_data.get('order', 0)
        )
        
        db.add(dept)
        await db.flush()  # 获取ID
        await db.commit()
        
        return respModel().ok_resp(dic_t={"id": dept.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    dept_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新部门"""
    try:
        dept_id = dept_data.get('id')
        result = await db.execute(select(Dept).where(Dept.id == dept_id))
        dept = result.scalars().first()
        if not dept:
            raise NotFoundException("部门不存在")
        
        # 更新字段
        if 'name' in dept_data:
            dept.name = dept_data['name']
        if 'parent_id' in dept_data:
            dept.parent_id = dept_data['parent_id']
        if 'leader' in dept_data:
            dept.leader = dept_data['leader']
        if 'phone' in dept_data:
            dept.phone = dept_data['phone']
        if 'email' in dept_data:
            dept.email = dept_data['email']
        if 'address' in dept_data:
            dept.address = dept_data['address']
        if 'order' in dept_data:
            dept.order = dept_data['order']
        
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
    id: int = Query(..., ge=1, description='部门ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除部门"""
    try:
        result = await db.execute(select(Dept).where(Dept.id == id))
        dept = result.scalars().first()
        if not dept:
            raise NotFoundException("部门不存在")
        
        # 检查是否有子部门
        has_children = await dept_crud.has_children(db, id)
        if has_children:
            raise BadRequestException("该部门下还有子部门，不能删除")
        
        await db.delete(dept)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
