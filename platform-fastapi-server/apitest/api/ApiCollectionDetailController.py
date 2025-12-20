"""
API测试集合详情Controller
"""
import json
from datetime import datetime
from typing import List

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiCollectionDetailModel import ApiCollectionDetail
from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..service.api_collection_detail_service import ApiCollectionDetailService
from ..schemas.api_collection_schema import ApiCollectionDetailCreate, ApiCollectionDetailUpdate

module_name = "ApiCollectionDetail"
module_model = ApiCollectionDetail
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试集合详情管理"])
logger = get_logger(__name__)


@module_route.get("/queryByCollectionId", summary="根据集合ID查询关联用例", dependencies=[Depends(check_permission("apitest:collectiondetail:query"))])
async def queryByCollectionId(collection_info_id: int = Query(...), session: Session = Depends(get_session)):
    """根据集合ID查询所有关联用例"""
    try:
        service = ApiCollectionDetailService(session)
        details = service.query_by_collection_id(collection_info_id)
        return respModel.ok_resp_list(lst=details, msg="查询成功")
    except Exception as e:
        logger.error(f"查询集合详情失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", summary="新增集合详情", dependencies=[Depends(check_permission("apitest:collectiondetail:add"))])
async def insert(detail: ApiCollectionDetailCreate, session: Session = Depends(get_session)):
    """新增集合详情"""
    try:
        service = ApiCollectionDetailService(session)
        data = service.create(
            collection_info_id=detail.collection_info_id,
            case_info_id=detail.case_info_id,
            run_order=detail.run_order,
            ddt_data=detail.ddt_data
        )
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增集合详情失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", summary="更新集合详情", dependencies=[Depends(check_permission("apitest:collectiondetail:edit"))])
async def update(detail: ApiCollectionDetailUpdate, session: Session = Depends(get_session)):
    """更新集合详情"""
    try:
        service = ApiCollectionDetailService(session)
        update_data = detail.model_dump(exclude_unset=True, exclude={'id'})
        updated = service.update(detail.id, update_data)
        if updated:
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="集合详情不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新集合详情失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败: {e}")


@module_route.delete("/delete", summary="删除集合详情", dependencies=[Depends(check_permission("apitest:collectiondetail:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除集合详情"""
    try:
        service = ApiCollectionDetailService(session)
        if service.delete(id):
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="集合详情不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除集合详情失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败: {e}")


@module_route.post("/batchAdd", summary="批量添加用例到集合", dependencies=[Depends(check_permission("apitest:collectiondetail:edit"))])
async def batchAdd(collection_info_id: int, case_ids: List[int], session: Session = Depends(get_session)):
    """批量添加用例到集合，自动提取数据驱动配置"""
    try:
        import re
        
        # 不需要参数化的字段
        skip_fields = {'URL', 'url', 'METHOD', 'method', 'Content-Type', 'content-type'}
        
        def extract_ddt_from_case(case_id: int) -> str:
            """从用例步骤中提取数据驱动配置"""
            variables = {}
            
            def extract_all_fields(data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key in skip_fields:
                            continue
                        if isinstance(value, dict):
                            extract_all_fields(value)
                        elif isinstance(value, list):
                            extract_all_fields(value)
                        elif isinstance(value, (str, int, float, bool)):
                            variables[key] = value if isinstance(value, str) else str(value)
                elif isinstance(data, list):
                    for item in data:
                        extract_all_fields(item)
            
            # 获取用例步骤
            steps = session.exec(
                select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == case_id)
            ).all()
            
            for step in steps:
                if step.step_data:
                    try:
                        step_dict = json.loads(step.step_data)
                        extract_all_fields(step_dict)
                    except:
                        pass
            
            # 获取用例名称
            case_info = session.get(ApiInfoCase, case_id)
            case_name = case_info.case_name if case_info else f"用例{case_id}"
            
            if variables:
                template = [{"desc": f"{case_name}_数据1", **variables}]
                return json.dumps(template, ensure_ascii=False)
            return None
        
        # 获取当前最大的run_order
        statement = select(module_model).where(module_model.collection_info_id == collection_info_id)
        existing = session.exec(statement).all()
        max_order = max([d.run_order for d in existing], default=0)
        
        # 批量添加，自动配置数据驱动
        for idx, case_id in enumerate(case_ids, 1):
            ddt_data = extract_ddt_from_case(case_id)
            detail = module_model(
                collection_info_id=collection_info_id,
                case_info_id=case_id,
                run_order=max_order + idx,
                ddt_data=ddt_data,
                create_time=datetime.now()
            )
            session.add(detail)
        
        session.commit()
        return respModel.ok_resp(msg=f"成功添加{len(case_ids)}个用例")
    except Exception as e:
        session.rollback()
        logger.error(f"批量添加用例失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.post("/batchUpdateOrder", summary="批量更新集合执行顺序", dependencies=[Depends(check_permission("apitest:collectiondetail:edit"))])
async def batchUpdateOrder(details: List[dict], session: Session = Depends(get_session)):
    """批量更新执行顺序"""
    try:
        for detail_data in details:
            detail_id = detail_data.get('id')
            run_order = detail_data.get('run_order')
            if detail_id and run_order is not None:
                statement = select(module_model).where(module_model.id == detail_id)
                db_detail = session.exec(statement).first()
                if db_detail:
                    db_detail.run_order = run_order
        session.commit()
        return respModel.ok_resp(msg="更新顺序成功")
    except Exception as e:
        session.rollback()
        logger.error(f"批量更新顺序失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败: {e}")


@module_route.get("/getDdtTemplate", summary="获取用例数据驱动模板")
async def getDdtTemplate(case_info_id: int = Query(...), session: Session = Depends(get_session)):
    """
    根据用例步骤数据提取变量，生成数据驱动模板
    """
    try:
        import re
        
        # 获取用例信息
        case_info = session.get(ApiInfoCase, case_info_id)
        if not case_info:
            return respModel.error_resp("用例不存在")
        
        # 获取用例步骤
        statement = select(ApiInfoCaseStep).where(
            ApiInfoCaseStep.case_info_id == case_info_id
        ).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()
        
        # 提取所有变量
        variables = {}  # {变量名: 示例值}
        variable_pattern = re.compile(r'\$\{?(\w+)\}?')
        
        # 不需要参数化的字段（通常是固定的）
        skip_fields = {'URL', 'url', 'METHOD', 'method', 'Content-Type', 'content-type'}
        
        def extract_all_fields(data):
            """递归提取所有字段作为变量"""
            if isinstance(data, dict):
                for key, value in data.items():
                    # 跳过不需要参数化的字段
                    if key in skip_fields:
                        continue
                    if isinstance(value, dict):
                        extract_all_fields(value)
                    elif isinstance(value, list):
                        extract_all_fields(value)
                    elif isinstance(value, (str, int, float, bool)):
                        # 将值转为字符串存储
                        variables[key] = value if isinstance(value, str) else str(value)
            elif isinstance(data, list):
                for item in data:
                    extract_all_fields(item)
        
        for step in steps:
            if step.step_data:
                try:
                    step_dict = json.loads(step.step_data)
                    # 提取所有字段
                    extract_all_fields(step_dict)
                except Exception as parse_err:
                    logger.warning(f"解析步骤数据失败: {parse_err}")
                
                # 同时查找 ${变量名} 格式的变量引用
                matches = variable_pattern.findall(step.step_data)
                for var in matches:
                    if var not in variables:
                        variables[var] = f"<{var}的值>"
        
        # 生成模板
        template_item = {"desc": f"{case_info.case_name}_数据1"}
        for var, value in variables.items():
            template_item[var] = value
        
        # 如果没有找到变量，添加示例
        if len(template_item) == 1:
            template_item["变量名1"] = "值1"
            template_item["变量名2"] = "值2"
        
        template = [template_item]
        
        return respModel.ok_resp(obj={
            "template": template,
            "variables": list(variables.keys()),
            "case_name": case_info.case_name
        })
    except Exception as e:
        logger.error(f"获取数据驱动模板失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取模板失败: {e}")
