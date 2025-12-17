import logging
from datetime import datetime
from typing import Dict, List, Optional

from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select, func

from ..model.AiModel import AiModel
from ..schemas.ai_model_schema import AiModelQuery, AiModelCreate, AiModelUpdate
from ..services.AiModelService import AiModelService

logger = logging.getLogger(__name__)

module_name = "AiModel"
module_route = APIRouter(prefix=f"/{module_name}", tags=["AI模型管理"])


# ==================== 模型同步请求模型 ====================
class SyncProviderRequest(BaseModel):
    """同步单个提供商模型请求"""
    provider: str = Field(..., description="提供商名称 (siliconflow, deepseek, openai, qwen, zhipuai)")
    api_key: Optional[str] = Field(default=None, description="API密钥，如果为空则从环境变量获取")
    update_existing: bool = Field(default=True, description="是否更新已存在的模型")


class SyncAllRequest(BaseModel):
    """同步所有提供商模型请求"""
    api_keys: Optional[Dict[str, str]] = Field(default=None, description="各提供商的API密钥字典")
    update_existing: bool = Field(default=True, description="是否更新已存在的模型")


# ==================== 基础CRUD接口 ====================
@module_route.post("/queryByPage", summary="分页查询AI模型")
async def queryByPage(query: AiModelQuery, session: Session = Depends(get_session)):
    datas, total, error = AiModelService.query_by_page(session, query)
    if error:
        return respModel.error_resp(error)
    return respModel.ok_resp_list(lst=datas, total=total)


@module_route.get("/queryById", summary="根据ID查询AI模型")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    data, error = AiModelService.query_by_id(session, id)
    if error:
        return respModel.error_resp(error)
    if data:
        return respModel.ok_resp(obj=data)
    else:
        return respModel.ok_resp(msg="查询成功,但是没有数据")


@module_route.get("/queryEnabled", summary="查询所有已启用的模型")
async def queryEnabled(session: Session = Depends(get_session)):
    datas, error = AiModelService.query_enabled(session)
    if error:
        return respModel.error_resp(error)
    return respModel.ok_resp_list(lst=datas, total=len(datas))


@module_route.post("/insert", summary="新增AI模型")
async def insert(model: AiModelCreate, session: Session = Depends(get_session)):
    model_id, error = AiModelService.insert(session, model)
    if error:
        return respModel.error_resp(msg=error)
    return respModel.ok_resp(msg="添加成功", dic_t={"id": model_id})


@module_route.put("/update", summary="更新AI模型")
async def update(model: AiModelUpdate, session: Session = Depends(get_session)):
    success, message = AiModelService.update(session, model)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.delete("/delete", summary="删除AI模型")
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    success, message = AiModelService.delete(session, id)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.post("/toggleStatus", summary="切换模型启用/禁用状态")
async def toggleStatus(id: int = Query(...), session: Session = Depends(get_session)):
    success, message = AiModelService.toggle_status(session, id)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


@module_route.post("/testConnection", summary="测试模型API连接")
async def testConnection(id: int = Query(...), session: Session = Depends(get_session)):
    success, message = await AiModelService.test_connection(session, id)
    if success:
        return respModel.ok_resp(msg=message)
    return respModel.error_resp(msg=message)


# ==================== 模型同步接口 ====================
@module_route.get("/sync/providers", summary="获取支持的提供商列表")
async def get_providers():
    """获取所有支持的模型提供商列表"""
    try:
        providers = []
        for provider, config in AiModelService.PROVIDER_CONFIGS.items():
            providers.append({
                "name": provider,
                "display_name": provider.title(),
                "api_url": config["api_url"],
                "api_key_env": config["api_key_env"],
                "default_api_url": config["default_api_url"]
            })
        return respModel.ok_resp(data=providers)
    except Exception as e:
        logger.error(f"获取提供商列表失败: {e}")
        return respModel.error_resp(f"获取提供商列表失败: {str(e)}")


@module_route.post("/sync/provider", summary="同步单个提供商的模型")
async def sync_provider(
    request: SyncProviderRequest, 
    session: Session = Depends(get_session)
):
    """
    从指定提供商同步模型列表
    
    **支持的提供商:**
    - siliconflow: SiliconFlow平台
    - deepseek: DeepSeek AI
    - openai: OpenAI
    - qwen: 阿里云通义千问
    - zhipuai: 智谱AI
    """
    try:
        result = await AiModelService.sync_models_from_provider(
            provider=request.provider,
            api_key=request.api_key,
            session=session,
            update_existing=request.update_existing
        )
        
        if result["success"]:
            logger.info(f"模型同步成功: {request.provider}, 新增 {result['added']} 个，更新 {result['updated']} 个")
            return respModel.ok_resp(data=result)
        else:
            logger.warning(f"模型同步失败: {request.provider}, {result['message']}")
            return respModel.error_resp(result["message"])
            
    except Exception as e:
        logger.error(f"同步模型失败: {request.provider}, {str(e)}")
        return respModel.error_resp(f"同步失败: {str(e)}")


@module_route.post("/sync/all", summary="同步所有提供商的模型")
async def sync_all_providers(
    request: SyncAllRequest,
    session: Session = Depends(get_session)
):
    """同步所有支持的提供商模型"""
    try:
        result = await AiModelService.sync_all_providers(
            api_keys=request.api_keys,
            session=session
        )
        
        if result["success"]:
            logger.info(f"全部模型同步完成: 新增 {result['total_added']} 个，更新 {result['total_updated']} 个")
            return respModel.ok_resp(data=result)
        else:
            logger.warning(f"全部模型同步失败: {result['message']}")
            return respModel.error_resp(result["message"])
            
    except Exception as e:
        logger.error(f"全部模型同步失败: {str(e)}")
        return respModel.error_resp(f"同步失败: {str(e)}")


@module_route.get("/sync/status", summary="获取同步状态")
async def get_sync_status(session: Session = Depends(get_session)):
    """获取模型同步状态和统计信息"""
    try:
        provider_stats = {}
        total_count = 0
        enabled_count = 0
        
        for provider in AiModelService.PROVIDER_CONFIGS.keys():
            count = session.exec(
                select(func.count(AiModel.id)).where(AiModel.provider == provider)
            ).one()
            
            enabled = session.exec(
                select(func.count(AiModel.id)).where(
                    (AiModel.provider == provider) & 
                    (AiModel.is_enabled == True)
                )
            ).one()
            
            provider_stats[provider] = {"total": count, "enabled": enabled}
            total_count += count
            enabled_count += enabled
        
        latest_sync = session.exec(
            select(AiModel.create_time).order_by(AiModel.create_time.desc())
        ).first()
        
        return respModel.ok_resp({
            "total_models": total_count,
            "enabled_models": enabled_count,
            "providers": provider_stats,
            "latest_sync": latest_sync.isoformat() if latest_sync else None
        })
        
    except Exception as e:
        logger.error(f"获取同步状态失败: {e}")
        return respModel.error_resp(f"获取状态失败: {str(e)}")
