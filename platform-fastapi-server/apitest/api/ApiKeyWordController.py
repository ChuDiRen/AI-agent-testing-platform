"""
关键字Controller - 已重构为使用Service层
"""
import json
import os
from datetime import datetime

from apitest.service.ApiKeywordService import ApiKeywordService
from config.dev_settings import settings
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiKeyWordModel import ApiKeyWord
from ..model.ApiOperationTypeModel import OperationType
from ..schemas.ApiKeywordSchema import ApiKeyWordQuery, ApiKeyWordCreate, ApiKeyWordUpdate, KeywordFileRequest

logger = get_logger(__name__)

# ==================== 配置常量 ====================
BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
YAML_DIR = settings.YAML_DIR
REPORT_DIR = settings.REPORT_DIR
LOG_DIR = settings.LOG_DIR

module_name = "ApiKeyWord"
module_model = ApiKeyWord
module_route = APIRouter(prefix=f"/{module_name}", tags=["API关键字管理"])

# ==================== 路由处理函数 ====================

@module_route.get("/queryAll", summary="查询所有关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryAll(session: Session = Depends(get_session)):
    """查询所有关键字"""
    try:
        service = ApiKeywordService(session)
        datas = service.query_all()
        return respModel.ok_resp_list(lst=datas, msg="查询成功")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/queryByPage", summary="分页查询关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryByPage(query: ApiKeyWordQuery, session: Session = Depends(get_session)):
    """分页查询关键字"""
    try:
        service = ApiKeywordService(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            keyword_name=query.name
        )
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.get("/queryById", summary="根据ID查询关键字")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询关键字"""
    try:
        service = ApiKeywordService(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.error_resp("关键字不存在")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/insert", summary="新增关键字", dependencies=[Depends(check_permission("apitest:keyword:add"))])
async def insert(keyword: ApiKeyWordCreate, session: Session = Depends(get_session)):
    """新增关键字"""
    try:
        service = ApiKeywordService(session)
        data = service.create(**keyword.model_dump())
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新关键字", dependencies=[Depends(check_permission("apitest:keyword:edit"))]) # 更新关键字
async def update(keyword: ApiKeyWordUpdate, session: Session = Depends(get_session)):
    try:
        # 检查关键字方法名是否与其他记录重复
        if keyword.keyword_fun_name:
            check_statement = select(module_model).where(module_model.keyword_fun_name == keyword.keyword_fun_name)
            existing = session.exec(check_statement).first()
            if existing and existing.id != keyword.id:
                return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入")
        statement = select(module_model).where(module_model.id == keyword.id)
        db_data = session.exec(statement).first()
        if db_data:
            update_data = keyword.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_data, key, value)
            session.commit()
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除关键字", dependencies=[Depends(check_permission("apitest:keyword:delete"))]) # 删除关键字
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.post("/keywordFile", summary="生成关键字文件", dependencies=[Depends(check_permission("apitest:keyword:generate"))]) # 生成关键字文件
async def keywordFile(request: KeywordFileRequest):
    try:
        file_name = request.keyword_fun_name
        keyword_value = request.keyword_value
        keywords_dir = str(settings.KEYWORDS_DIR)
        os.makedirs(keywords_dir, exist_ok=True)
        with open(f'{keywords_dir}/{file_name}.py', 'w', encoding="utf-8") as f:
            f.write(keyword_value)
        return respModel.ok_resp(msg="生成文件成功", dic_t={"id": file_name})
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.get("/queryByOperationType", summary="根据操作类型查询关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))]) # 根据操作类型ID查询关键字列表
async def queryByOperationType(operation_type_id: int = Query(...), session: Session = Depends(get_session)):
    """根据操作类型ID查询关键字列表"""
    try:
        statement = select(module_model).where(module_model.operation_type_id == operation_type_id)
        datas = session.exec(statement).all()
        result = [
            {
                "id": data.id,
                "name": data.name,
                "keyword_fun_name": data.keyword_fun_name,
                "keyword_desc": data.keyword_desc,
                "operation_type_id": data.operation_type_id,
                "is_enabled": data.is_enabled
            } for data in datas
        ]
        return respModel.ok_resp_list(lst=result, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getKeywordFields", summary="获取关键字字段描述", dependencies=[Depends(check_permission("apitest:keyword:query"))]) # 获取关键字的字段描述
async def getKeywordFields(keyword_id: int = Query(...), session: Session = Depends(get_session)):
    """获取关键字的字段描述（解析keyword_desc或从代码中提取）"""
    try:
        import json
        import re
        
        # 查询关键字
        keyword = session.get(module_model, keyword_id)
        if not keyword:
            return respModel.error_resp("关键字不存在")
        
        # 尝试解析keyword_desc为JSON
        try:
            if keyword.keyword_desc:
                fields = json.loads(keyword.keyword_desc)
                # 这里 keyword_desc 本身就是字段定义列表，直接以数组形式返回
                if isinstance(fields, list):
                    return respModel.ok_resp_simple(lst=fields, msg="查询成功")
                else:
                    return respModel.ok_resp_simple(lst=[fields], msg="查询成功")
        except json.JSONDecodeError:
            # 不是JSON格式，尝试从代码中提取
            pass
        
        # 从keyword_value（函数代码）中提取参数
        fields = []
        if keyword.keyword_value:
            # 匹配 kwargs.get("PARAM_NAME", default) 模式
            pattern = r'kwargs\.get\s*\(\s*["\'](\w+)["\']\s*(?:,\s*([^)]+))?\)'
            matches = re.findall(pattern, keyword.keyword_value)
            
            for param_name, default_value in matches:
                field = {
                    "name": param_name,
                    "type": "string",
                    "required": default_value.strip() == "None" if default_value else True,
                    "description": f"参数: {param_name}",
                    "default": "" if not default_value or default_value.strip() == "None" else default_value.strip().strip("'\"")
                }
                fields.append(field)
        
        # 最终返回字段定义数组
        if fields:
            return respModel.ok_resp_simple(lst=fields, msg="查询成功")
        else:
            return respModel.ok_resp_simple(lst=[], msg="该关键字没有字段描述")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")
