import logging
from datetime import datetime

import httpx
from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import select, Session, func

from ..model.AiModel import AiModel
from ..schemas.ai_model_schema import AiModelQuery, AiModelCreate, AiModelUpdate

logger = logging.getLogger(__name__)

module_name = "AiModel" # 模块名称
module_model = AiModel
module_route = APIRouter(prefix=f"/{module_name}", tags=["AI模型管理"])


@module_route.post("/queryByPage", summary="分页查询AI模型") # 分页查询AI模型
async def queryByPage(query: AiModelQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        # 按提供商过滤
        if query.provider:
            statement = statement.where(module_model.provider == query.provider)
        
        # 按状态过滤
        if query.is_enabled is not None:
            statement = statement.where(module_model.is_enabled == query.is_enabled)
        
        statement = statement.order_by(module_model.create_time.desc()).limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(func.count(module_model.id))
        if query.provider:
            count_statement = count_statement.where(module_model.provider == query.provider)
        if query.is_enabled is not None:
            count_statement = count_statement.where(module_model.is_enabled == query.is_enabled)
        total = session.exec(count_statement).one()
        
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryById", summary="根据ID查询AI模型") # 根据ID查询AI模型
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryEnabled", summary="查询所有已启用的模型") # 查询所有已启用的模型
async def queryEnabled(session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.is_enabled == True).order_by(module_model.create_time)
        datas = session.exec(statement).all()
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/insert", summary="新增AI模型") # 新增AI模型
async def insert(model: AiModelCreate, session: Session = Depends(get_session)):
    try:
        # 检查模型代码是否重复
        existing = session.exec(
            select(module_model).where(module_model.model_code == model.model_code)
        ).first()
        if existing:
            return respModel.error_resp(msg="模型代码已存在")
        
        data = module_model(**model.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        logger.info(f"新增AI模型成功: {data.model_name}")
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新AI模型") # 更新AI模型
async def update(model: AiModelUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == model.id)
        db_model = session.exec(statement).first()
        if db_model:
            update_data = model.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_model, key, value)
            db_model.modify_time = datetime.now()
            session.commit()
            logger.info(f"更新AI模型成功: {db_model.model_name}")
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="AI模型不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除AI模型") # 删除AI模型
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            logger.info(f"删除AI模型成功: {data.model_name}")
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="AI模型不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败，请联系管理员:{e}")


@module_route.post("/toggleStatus", summary="切换模型启用/禁用状态") # 切换模型启用/禁用状态
async def toggleStatus(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        model = session.get(module_model, id)
        if not model:
            return respModel.error_resp(msg="AI模型不存在")
        
        model.is_enabled = not model.is_enabled
        model.modify_time = datetime.now()
        session.commit()
        
        status = "启用" if model.is_enabled else "禁用"
        logger.info(f"{status}AI模型成功: {model.model_name}")
        return respModel.ok_resp(msg=f"已{status}")
    except Exception as e:
        session.rollback()
        logger.error(f"切换状态失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"操作失败:{e}")


@module_route.post("/testConnection", summary="测试模型API连接") # 测试模型API连接
async def testConnection(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        model = session.get(module_model, id)
        if not model:
            return respModel.error_resp(msg="AI模型不存在")
        
        if not model.api_key:
            return respModel.error_resp(msg="请先配置API Key")
        
        # 发送测试请求
        test_message = [{"role": "user", "content": "Hi"}]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # SiliconFlow平台 - 使用OpenAI兼容接口
            if model.provider == "siliconflow" or "siliconflow" in model.api_url:
                api_url = model.api_url.rstrip('/') + "/chat/completions"
                response = await client.post(
                    api_url,
                    headers={
                        "Authorization": f"Bearer {model.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model.model_code,
                        "messages": test_message,
                        "max_tokens": 5
                    }
                )
            elif model.provider == "deepseek" or "deepseek" in model.api_url:
                api_url = model.api_url.rstrip('/') + "/chat/completions"
                response = await client.post(
                    api_url,
                    headers={"Authorization": f"Bearer {model.api_key}"},
                    json={
                        "model": model.model_code,
                        "messages": test_message,
                        "max_tokens": 5
                    }
                )
            elif model.provider == "qwen" or "dashscope" in model.api_url:
                api_url = model.api_url.rstrip('/') + "/chat/completions"
                response = await client.post(
                    api_url,
                    headers={"Authorization": f"Bearer {model.api_key}"},
                    json={
                        "model": model.model_code,
                        "messages": test_message,
                        "max_tokens": 5
                    }
                )
            elif model.provider == "openai" or "openai" in model.api_url:
                api_url = model.api_url.rstrip('/') + "/chat/completions"
                response = await client.post(
                    api_url,
                    headers={"Authorization": f"Bearer {model.api_key}"},
                    json={
                        "model": model.model_code,
                        "messages": test_message,
                        "max_tokens": 5
                    }
                )
            else:
                # 通用OpenAI兼容接口
                api_url = model.api_url.rstrip('/') + "/chat/completions"
                response = await client.post(
                    api_url,
                    headers={
                        "Authorization": f"Bearer {model.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model.model_code,
                        "messages": test_message,
                        "max_tokens": 5
                    }
                )
            
            if response.status_code == 200:
                logger.info(f"连接测试成功: {model.model_name}")
                return respModel.ok_resp(msg="连接测试成功")
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("error", {}).get("message", "") or str(error_data)
                except:
                    error_detail = response.text[:200]
                logger.warning(f"连接测试失败: {model.model_name}, status: {response.status_code}, detail: {error_detail}")
                return respModel.error_resp(msg=f"连接失败({response.status_code}): {error_detail}")
    
    except httpx.TimeoutException:
        logger.error(f"连接超时: {model.model_name}")
        return respModel.error_resp(msg="连接超时，请检查网络或API地址")
    except httpx.ConnectError as e:
        logger.error(f"连接错误: {model.model_name}, {e}")
        return respModel.error_resp(msg="无法连接到API服务器，请检查API地址")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"测试失败: {str(e)}")


