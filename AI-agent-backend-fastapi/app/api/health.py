"""健康检查接口"""
from fastapi import APIRouter
from datetime import datetime, timezone
from app.core.database import check_db_health
from app.core.config import settings
from app.schemas.common import APIResponse

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("", response_model=APIResponse)
async def health_check() -> APIResponse:
    """
    基础健康检查
    
    检查服务是否运行正常
    """
    return APIResponse(
        message="服务运行正常",
        data={
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )


@router.get("/detailed", response_model=APIResponse)
async def detailed_health_check() -> APIResponse:
    """
    详细健康检查
    
    检查各个组件的健康状态
    """
    # 检查数据库
    db_healthy = await check_db_health()
    
    # 检查 Redis (Token黑名单)
    redis_healthy = False
    try:
        from app.core.token_blacklist import token_blacklist
        redis_healthy = token_blacklist.redis_client is not None and token_blacklist.redis_client.ping()
    except Exception:
        redis_healthy = False
    
    # 整体状态
    overall_status = "healthy" if (db_healthy and redis_healthy) else "degraded"
    
    components = {
        "database": {
            "status": "healthy" if db_healthy else "unhealthy",
            "message": "数据库连接正常" if db_healthy else "数据库连接失败"
        },
        "redis": {
            "status": "healthy" if redis_healthy else "unhealthy",
            "message": "Redis连接正常" if redis_healthy else "Redis连接失败"
        }
    }
    
    return APIResponse(
        message=f"服务状态: {overall_status}",
        data={
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "components": components
        }
    )


@router.get("/ready")
async def readiness_check():
    """
    就绪检查 (Kubernetes readiness probe)
    
    检查服务是否准备好接收流量
    """
    db_healthy = await check_db_health()
    
    if db_healthy:
        return {"status": "ready"}
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="服务未就绪"
        )


@router.get("/live")
async def liveness_check():
    """
    存活检查 (Kubernetes liveness probe)
    
    检查服务是否存活
    """
    return {"status": "alive"}

