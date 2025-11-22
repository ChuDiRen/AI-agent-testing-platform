import logging
from datetime import datetime

from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import select, Session, func

from ..model.PromptTemplate import PromptTemplate
from ..schemas.prompt_template_schema import PromptTemplateQuery, PromptTemplateCreate, PromptTemplateUpdate

logger = logging.getLogger(__name__)

module_name = "PromptTemplate" # 模块名称
module_model = PromptTemplate
module_route = APIRouter(prefix=f"/{module_name}", tags=["提示词模板管理"])


@module_route.post("/queryByPage", summary="分页查询提示词模板") # 分页查询提示词模板
def queryByPage(query: PromptTemplateQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        # 按测试类型过滤
        if query.test_type:
            statement = statement.where(module_model.test_type == query.test_type)
        
        # 按模板类型过滤
        if query.template_type:
            statement = statement.where(module_model.template_type == query.template_type)
        
        # 按状态过滤
        if query.is_active is not None:
            statement = statement.where(module_model.is_active == query.is_active)
        
        statement = statement.order_by(module_model.create_time.desc()).limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(func.count(module_model.id))
        if query.test_type:
            count_statement = count_statement.where(module_model.test_type == query.test_type)
        if query.template_type:
            count_statement = count_statement.where(module_model.template_type == query.template_type)
        if query.is_active is not None:
            count_statement = count_statement.where(module_model.is_active == query.is_active)
        total = session.exec(count_statement).one()
        
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryById", summary="根据ID查询提示词模板") # 根据ID查询提示词模板
def queryById(id: int = Query(...), session: Session = Depends(get_session)):
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


@module_route.get("/queryByType", summary="按测试类型获取所有激活的模板") # 按测试类型获取所有激活的模板
def queryByType(testType: str = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(
            (module_model.test_type == testType) &
            (module_model.is_active == True)
        ).order_by(module_model.create_time)
        datas = session.exec(statement).all()
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryAll", summary="查询所有提示词模板") # 查询所有提示词模板
def queryAll(session: Session = Depends(get_session)):
    try:
        statement = select(module_model).order_by(module_model.create_time.desc())
        datas = session.exec(statement).all()
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/insert", summary="新增提示词模板") # 新增提示词模板
def insert(template: PromptTemplateCreate, session: Session = Depends(get_session)):
    try:
        data = module_model(**template.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        logger.info(f"新增提示词模板成功: {data.name}")
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新提示词模板") # 更新提示词模板
def update(template: PromptTemplateUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == template.id)
        db_template = session.exec(statement).first()
        if db_template:
            update_data = template.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_template, key, value)
            db_template.modify_time = datetime.now()
            session.commit()
            logger.info(f"更新提示词模板成功: {db_template.name}")
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="提示词模板不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除提示词模板") # 删除提示词模板
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            logger.info(f"删除提示词模板成功: {data.name}")
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="提示词模板不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败，请联系管理员:{e}")


@module_route.post("/toggleActive", summary="切换模板激活/停用状态") # 切换模板激活/停用状态
def toggleActive(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        template = session.get(module_model, id)
        if not template:
            return respModel.error_resp(msg="提示词模板不存在")
        
        template.is_active = not template.is_active
        template.modify_time = datetime.now()
        session.commit()
        
        status = "激活" if template.is_active else "停用"
        logger.info(f"{status}提示词模板成功: {template.name}")
        return respModel.ok_resp(msg=f"已{status}")
    except Exception as e:
        session.rollback()
        logger.error(f"切换状态失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"操作失败:{e}")


@module_route.get("/queryByTestType", summary="按测试类型查询模板") # 按测试类型查询模板
def queryByTestType(test_type: str = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(
            module_model.test_type == test_type,
            module_model.is_active == True
        ).order_by(module_model.create_time)
        datas = session.exec(statement).all()
        return respModel.ok_resp_list(lst=datas, total=len(datas))
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
