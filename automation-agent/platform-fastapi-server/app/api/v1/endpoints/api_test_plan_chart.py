"""
API 测试计划图表端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.api_test_plan_chart import ApiTestPlanChart
from app.core.resp_model import RespModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func

router = APIRouter(prefix="/ApiTestPlanChart", tags=["API测试计划图表"])


@router.get("/queryAll", response_model=ResponseModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart))
        items = result.scalars().all()
        return RespModel.success(data=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=ResponseModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_id: Optional[int] = Query(None, description='项目ID'),
    chart_name: Optional[str] = Query(None, description='图表名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询测试计划图表"""
    try:
        query = select(ApiTestPlanChart)
        
        # 添加筛选条件
        if project_id:
            query = query.where(ApiTestPlanChart.project_id == project_id)
        
        if chart_name:
            query = query.where(ApiTestPlanChart.chart_name.like(f"%{chart_name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return RespModel.success(data=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=ResponseModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='测试计划图表ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart).where(ApiTestPlanChart.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("测试计划图表不存在")
        return RespModel.success(data=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=ResponseModel)
async def insert(
    *,
    chart_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建测试计划图表"""
    try:
        chart = ApiTestPlanChart(**chart_data)
        db.add(chart)
        await db.flush()
        await db.commit()
        return RespModel.success(data={"id": chart.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=ResponseModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='测试计划图表ID'),
    chart_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart).where(ApiTestPlanChart.id == id))
        chart = result.scalars().first()
        if not chart:
            raise NotFoundException("测试计划图表不存在")
        
        # 更新字段
        for field, value in chart_data.items():
            if hasattr(chart, field):
                setattr(chart, field, value)
        
        await db.commit()
        return RespModel.success(msg="修改成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=ResponseModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='测试计划图表ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart).where(ApiTestPlanChart.id == id))
        chart = result.scalars().first()
        if not chart:
            raise NotFoundException("测试计划图表不存在")
        
        await db.delete(chart)
        await db.commit()
        return RespModel.success(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/queryPlanCount", response_model=ResponseModel)
async def query_plan_count(
    *,
    coll_id: str = Query(..., description='测试计划ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询测试计划执行次数"""
    try:
        from app.models.api_history import ApiHistory
        
        # 根据coll_id查询执行数据条数
        result = await db.execute(
            select(ApiHistory).where(ApiHistory.collection_info_id == coll_id)
        )
        count = len(result.scalars().all())
        
        return RespModel.success(msg="查询成功", data=count)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/queryCaseCount", response_model=ResponseModel)
async def query_case_count(
    *,
    coll_id: str = Query(..., description='测试计划ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询测试计划用例数量"""
    try:
        # 查询最后一次测试计划执行记录
        result = await db.execute(
            select(ApiTestPlanChart)
            .where(ApiTestPlanChart.collection_info_id == coll_id)
            .order_by(ApiTestPlanChart.id.desc())
        )
        last_data = result.scalars().first()
        
        if not last_data:
            return RespModel.success(msg="未找到测试计划执行记录", data=0)
        
        # 模拟用例数量计算
        case_count = 10  # 这里可以根据实际业务逻辑计算
        
        return RespModel.success(msg="查询成功", data=case_count)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/queryPassRate", response_model=ResponseModel)
async def query_pass_rate(
    *,
    coll_id: str = Query(..., description='测试计划ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询测试计划通过率"""
    try:
        # 模拟通过率计算
        # 实际应该查询HistoryInfo表统计pass和total数量
        pass_count = 8
        total_count = 10
        
        pass_rate = 0
        if total_count > 0:
            pass_rate = round((pass_count / total_count) * 100, 2)
        
        return RespModel.success(msg="查询成功", data=pass_rate)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/queryPlanTrend", response_model=ResponseModel)
async def query_plan_trend(
    *,
    coll_id: str = Query(..., description='测试计划ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询测试计划执行趋势"""
    try:
        # 模拟趋势数据
        trend_data = []
        
        # 生成最近10次执行结果的趋势数据
        for i in range(10):
            trend_data.append({
                "date": f"2024-01-{10-i:02d}",
                "total": 10,
                "passed": 8 + (i % 3),
                "failed": 2 - (i % 2),
                "broken": (i % 2),
                "skipped": 0,
                "unknown": 0
            })
        
        return RespModel.success(msg="查询成功", data=trend_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/queryPlanTime", response_model=ResponseModel)
async def query_plan_time(
    *,
    coll_id: str = Query(..., description='测试计划ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询测试计划执行时间"""
    try:
        # 模拟时间数据
        time_data = []
        
        # 生成最近10次执行时间数据
        for i in range(10):
            time_data.append({
                "date": f"2024-01-{10-i:02d} {12+i:02d}:00:00",
                "duration": 120 + (i * 10)  # 模拟执行时间（秒）
            })
        
        return RespModel.success(msg="查询成功", data=time_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/queryFailTop5", response_model=ResponseModel)
async def query_fail_top5(
    *,
    coll_id: str = Query(..., description='测试计划ID'),
    db: AsyncSession = Depends(get_db)
):
    """查询失败率最高的5个用例"""
    try:
        # 模拟失败用例数据
        result = [
            {"name": "用户登录测试", "fail_count": 5},
            {"name": "数据查询测试", "fail_count": 3},
            {"name": "表单提交测试", "fail_count": 2},
            {"name": "文件上传测试", "fail_count": 2},
            {"name": "权限验证测试", "fail_count": 1}
        ]
        
        return RespModel.success(msg="查询成功", data=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
