import os
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.resp_model import respModel
from core.logger import get_logger

logger = get_logger(__name__)
from apitest.model.ApiKeyWordModel import ApiKeyWord
from apitest.schemas.api_keyword_schema import ApiKeyWordQuery, ApiKeyWordCreate, ApiKeyWordUpdate, KeywordFileRequest
from core.database import get_session
from core.time_utils import TimeFormatter
from config.dev_settings import settings
from datetime import datetime

module_name = "ApiKeyWord" # 模块名称
module_model = ApiKeyWord
module_route = APIRouter(prefix=f"/{module_name}", tags=["API关键字管理"])

@module_route.get("/queryAll") # 查询所有关键字
def queryAll(session: Session = Depends(get_session)):
    statement = select(module_model)
    datas = session.exec(statement).all()
    return respModel.ok_resp_list(lst=datas, msg="查询成功")

@module_route.post("/queryByPage") # 分页查询关键字
def queryByPage(query: ApiKeyWordQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        # 添加关键字名称模糊搜索条件
        if query.name:
            statement = statement.where(module_model.name.like(f'%{query.name}%'))
        # 添加操作类型筛选条件
        if query.operation_type_id and query.operation_type_id > 0:
            statement = statement.where(module_model.operation_type_id == query.operation_type_id)
        # 添加页面筛选条件
        if query.page_id and query.page_id > 0:
            statement = statement.where(module_model.page_id == query.page_id)
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        count_statement = select(module_model)
        if query.name:
            count_statement = count_statement.where(module_model.name.like(f'%{query.name}%'))
        if query.operation_type_id and query.operation_type_id > 0:
            count_statement = count_statement.where(module_model.operation_type_id == query.operation_type_id)
        if query.page_id and query.page_id > 0:
            count_statement = count_statement.where(module_model.page_id == query.page_id)
        total = len(session.exec(count_statement).all())
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById") # 根据ID查询关键字
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert") # 新增关键字
def insert(keyword: ApiKeyWordCreate, session: Session = Depends(get_session)):
    try:
        # 检查关键字方法名是否重复
        statement = select(module_model).where(module_model.keyword_fun_name == keyword.keyword_fun_name)
        existing = session.exec(statement).first()
        if existing:
            return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入")
        data = module_model(**keyword.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update") # 更新关键字
def update(keyword: ApiKeyWordUpdate, session: Session = Depends(get_session)):
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

@module_route.delete("/delete") # 删除关键字
def delete(id: int = Query(...), session: Session = Depends(get_session)):
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

@module_route.post("/keywordFile") # 生成关键字文件
def keywordFile(request: KeywordFileRequest):
    try:
        file_name = request.keyword_fun_name
        keyword_value = request.keyword_value
        key_words_dir = settings.KEY_WORDS_DIR
        os.makedirs(key_words_dir, exist_ok=True)
        with open(f'{key_words_dir}/{file_name}.py', 'w', encoding="utf-8") as f:
            f.write(keyword_value)
        return respModel.ok_resp(msg="生成文件成功", dic_t={"id": file_name})
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")