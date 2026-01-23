"""
审计日志中间件
自动记录用户的操作请求
"""
import time
import json
from typing import Optional
from fastapi import Request, Response
from app.core.logger import logger
from app.crud.audit_log import audit_log
from app.db.session import get_db


# 不需要审计的路径白名单
AUDIT_WHITELIST = [
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/login",
    "/favicon.ico",
]


async def create_audit_log(
    request: Request,
    response: Response,
    process_time: float,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    error_msg: Optional[str] = None
):
    """创建审计日志记录"""
    try:
        # 构建审计日志数据
        audit_data = {
            "user_id": user_id,
            "username": username,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.url.query) if request.url.query else None,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "status_code": response.status_code,
            "process_time": round(process_time * 1000, 2),  # 转换为毫秒
            "error_msg": error_msg,
        }
        
        # 尝试获取请求体（对于 POST/PUT/PATCH 请求）
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 注意：读取请求体会导致后续无法再读取，这里仅作示例
                # 实际使用时需要在依赖中缓存请求体
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode("utf-8", errors="ignore")
                    # 尝试解析为 JSON 格式化
                    try:
                        body_json = json.loads(body_str)
                        # 过滤敏感字段
                        if "password" in body_json:
                            body_json["password"] = "******"
                        if "old_password" in body_json:
                            body_json["old_password"] = "******"
                        if "new_password" in body_json:
                            body_json["new_password"] = "******"
                        audit_data["request_body"] = json.dumps(body_json, ensure_ascii=False)
                    except:
                        audit_data["request_body"] = body_str[:1000]  # 限制长度
            except Exception as e:
                logger.warning(f"读取请求体失败: {e}")
                # 不要设置 request_body，避免错误
                pass
        
        # 获取数据库会话
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # 创建审计日志
            audit_log.create(db, obj_in=audit_data)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"保存审计日志失败: {e}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"创建审计日志异常: {e}")


def create_audit_middleware(app):
    """创建并注册审计日志中间件"""
    
    @app.middleware("http")
    async def audit_log_middleware(request: Request, call_next):
        """审计日志中间件"""
        start_time = time.time()
        
        # 检查是否在白名单中
        if request.url.path in AUDIT_WHITELIST:
            return await call_next(request)
        
        # 获取用户信息（从 request.state 中获取，由 Token 验证中间件设置）
        user_id = getattr(request.state, "user_id", None)
        username = getattr(request.state, "username", None)
        
        # 记录请求
        logger.info(f"Request: {request.method} {request.url.path} by {username or 'anonymous'}")
        
        # 调用下一个中间件或路由处理
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 异步创建审计日志（不阻塞响应）
            # 注意：这里使用后台任务会更高效，但为了简化，我们直接调用
            await create_audit_log(
                request=request,
                response=response,
                process_time=process_time,
                user_id=user_id,
                username=username,
            )
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"请求处理失败: {e}")
            
            # 记录错误审计日志
            from fastapi import status
            
            # 构造错误响应对象
            error_response = Response(
                content=json.dumps({"code": 500, "msg": "Internal Server Error", "data": None}),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/json"
            )
            
            # 记录审计日志
            await create_audit_log(
                request=request,
                response=error_response,
                process_time=process_time,
                user_id=user_id,
                username=username,
                error_msg=str(e)
            )
            
            raise


# 白名单管理函数
def add_audit_whitelist(path: str):
    """添加审计白名单路径"""
    if path not in AUDIT_WHITELIST:
        AUDIT_WHITELIST.append(path)


def remove_audit_whitelist(path: str):
    """移除审计白名单路径"""
    if path in AUDIT_WHITELIST:
        AUDIT_WHITELIST.remove(path)


def is_whitelisted(path: str) -> bool:
    """检查路径是否在白名单中"""
    return path in AUDIT_WHITELIST
