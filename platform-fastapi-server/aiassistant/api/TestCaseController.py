import json
import logging
from datetime import datetime

import yaml
from core.database import get_session
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import select, Session, func

from ..model.TestCaseModel import TestCase
from ..schemas.test_case_schema import TestCaseQuery, TestCaseCreate, TestCaseUpdate, BatchInsertRequest

logger = logging.getLogger(__name__)

module_name = "TestCase" # 模块名称
module_model = TestCase
module_route = APIRouter(prefix=f"/{module_name}", tags=["测试用例管理"])


@module_route.post("/queryByPage", summary="分页查询测试用例") # 分页查询测试用例
def queryByPage(query: TestCaseQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        # 按项目过滤
        if query.project_id:
            statement = statement.where(module_model.project_id == query.project_id)
        
        # 按测试类型过滤
        if query.test_type:
            statement = statement.where(module_model.test_type == query.test_type)
        
        # 按优先级过滤
        if query.priority:
            statement = statement.where(module_model.priority == query.priority)
        
        statement = statement.order_by(module_model.create_time.desc()).limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(func.count(module_model.id))
        if query.project_id:
            count_statement = count_statement.where(module_model.project_id == query.project_id)
        if query.test_type:
            count_statement = count_statement.where(module_model.test_type == query.test_type)
        if query.priority:
            count_statement = count_statement.where(module_model.priority == query.priority)
        total = session.exec(count_statement).one()
        
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryById", summary="根据ID查询测试用例") # 根据ID查询测试用例
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


@module_route.post("/insert", summary="新增测试用例") # 新增测试用例
def insert(case: TestCaseCreate, session: Session = Depends(get_session)):
    try:
        data = module_model(**case.model_dump(), create_time=datetime.now(), modify_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        logger.info(f"新增测试用例成功: {data.case_name}")
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.post("/batchInsert", summary="批量插入测试用例") # 批量插入测试用例
def batchInsert(req: BatchInsertRequest, session: Session = Depends(get_session)):
    try:
        created_cases = []
        for case_data in req.test_cases:
            test_case = module_model(
                **case_data.model_dump(),
                project_id=req.project_id,
                create_time=datetime.now(),
                modify_time=datetime.now()
            )
            session.add(test_case)
            created_cases.append(test_case)
        
        session.commit()
        for case in created_cases:
            session.refresh(case)
        
        logger.info(f"批量插入{len(created_cases)}个测试用例成功")
        return respModel.ok_resp(msg=f"成功创建{len(created_cases)}个测试用例", dic_t={"count": len(created_cases)})
    except Exception as e:
        session.rollback()
        logger.error(f"批量插入失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量创建失败:{e}")


@module_route.put("/update", summary="更新测试用例") # 更新测试用例
def update(case: TestCaseUpdate, session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == case.id)
        db_case = session.exec(statement).first()
        if db_case:
            update_data = case.model_dump(exclude_unset=True, exclude={'id'})
            for key, value in update_data.items():
                setattr(db_case, key, value)
            db_case.modify_time = datetime.now()
            session.commit()
            logger.info(f"更新测试用例成功: {db_case.case_name}")
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="测试用例不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除测试用例") # 删除测试用例
def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            logger.info(f"删除测试用例成功: {data.case_name}")
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="测试用例不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败，请联系管理员:{e}")


@module_route.get("/exportYaml", summary="导出单个测试用例为YAML") # 导出单个测试用例为YAML
def exportYaml(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        test_case = session.get(module_model, id)
        if not test_case:
            return respModel.error_resp(msg="测试用例不存在")
        
        # 构建YAML数据
        yaml_data = {
            "name": test_case.case_name,
            "priority": test_case.priority,
            "test_type": test_case.test_type,
            "precondition": test_case.precondition,
            "test_steps": json.loads(test_case.test_steps) if test_case.test_steps else [],
            "expected_result": test_case.expected_result,
            "test_data": json.loads(test_case.test_data) if test_case.test_data else None
        }
        
        # 转换为YAML
        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"导出测试用例YAML成功: {test_case.case_name}")
        return Response(
            content=yaml_content,
            media_type="application/x-yaml",
            headers={"Content-Disposition": f"attachment; filename={test_case.case_name}.yaml"}
        )
    except Exception as e:
        logger.error(f"导出失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"导出失败:{e}")


@module_route.post("/exportBatchYaml", summary="批量导出测试用例为YAML") # 批量导出测试用例为YAML
def exportBatchYaml(case_ids: list[int], session: Session = Depends(get_session)):
    try:
        test_cases = session.exec(
            select(module_model).where(module_model.id.in_(case_ids))
        ).all()
        
        if not test_cases:
            return respModel.error_resp(msg="未找到测试用例")
        
        # 构建YAML数据列表
        yaml_data_list = []
        for test_case in test_cases:
            yaml_data = {
                "name": test_case.case_name,
                "priority": test_case.priority,
                "test_type": test_case.test_type,
                "precondition": test_case.precondition,
                "test_steps": json.loads(test_case.test_steps) if test_case.test_steps else [],
                "expected_result": test_case.expected_result,
                "test_data": json.loads(test_case.test_data) if test_case.test_data else None
            }
            yaml_data_list.append(yaml_data)
        
        # 转换为YAML
        yaml_content = yaml.dump(yaml_data_list, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"批量导出{len(test_cases)}个测试用例YAML成功")
        return Response(
            content=yaml_content,
            media_type="application/x-yaml",
            headers={"Content-Disposition": f"attachment; filename=test_cases_batch.yaml"}
        )
    except Exception as e:
        logger.error(f"批量导出失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"导出失败:{e}")
