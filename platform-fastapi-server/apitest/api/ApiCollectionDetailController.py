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
from ..schemas.api_collection_schema import ApiCollectionDetailCreate, ApiCollectionDetailUpdate

module_name = "ApiCollectionDetail"
module_model = ApiCollectionDetail
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试集合详情管理"])
logger = get_logger(__name__)


@module_route.get("/queryByCollectionId", summary="根据集合ID查询关联用例", dependencies=[Depends(check_permission("apitest:collectiondetail:query"))])
async def queryByCollectionId(collection_info_id: int = Query(...), session: Session = Depends(get_session)):
    """根据集合ID查询所有关联用例"""
    try:
        statement = select(module_model).where(
            module_model.collection_info_id == collection_info_id
        ).order_by(module_model.run_order)
        details = session.exec(statement).all()
        return respModel.ok_resp_list(lst=details, msg="查询成功")
    except Exception as e:
        logger.error(f"查询集合详情失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")


@module_route.post("/insert", summary="新增集合详情", dependencies=[Depends(check_permission("apitest:collectiondetail:add"))])
async def insert(detail: ApiCollectionDetailCreate, session: Session = Depends(get_session)):
    """新增集合详情"""
    try:
        # 将字典转换为JSON字符串
        detail_data = detail.model_dump()
        if detail_data.get('ddt_data'):
            detail_data['ddt_data'] = json.dumps(detail_data['ddt_data'], ensure_ascii=False)
        
        data = module_model(**detail_data, create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增集合详情失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败: {e}")


@module_route.put("/update", summary="更新集合详情", dependencies=[Depends(check_permission("apitest:collectiondetail:edit"))])
async def update(detail: ApiCollectionDetailUpdate, session: Session = Depends(get_session)):
    """更新集合详情"""
    try:
        statement = select(module_model).where(module_model.id == detail.id)
        db_detail = session.exec(statement).first()
        if db_detail:
            update_data = detail.model_dump(exclude_unset=True, exclude={'id'})
            # 处理ddt_data
            if 'ddt_data' in update_data and update_data['ddt_data']:
                update_data['ddt_data'] = json.dumps(update_data['ddt_data'], ensure_ascii=False)
            
            for key, value in update_data.items():
                setattr(db_detail, key, value)
            session.commit()
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
        statement = select(module_model).where(module_model.id == id)
        data = session.exec(statement).first()
        if data:
            session.delete(data)
            session.commit()
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="集合详情不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除集合详情失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败: {e}")


@module_route.post("/batchAdd", summary="批量添加用例到集合", dependencies=[Depends(check_permission("apitest:collectiondetail:edit"))])
async def batchAdd(collection_info_id: int, case_ids: List[int], session: Session = Depends(get_session)):
    """批量添加用例到集合"""
    try:
        # 获取当前最大的run_order
        statement = select(module_model).where(module_model.collection_info_id == collection_info_id)
        existing = session.exec(statement).all()
        max_order = max([d.run_order for d in existing], default=0)
        
        # 批量添加
        for idx, case_id in enumerate(case_ids, 1):
            detail = module_model(
                collection_info_id=collection_info_id,
                case_info_id=case_id,
                run_order=max_order + idx,
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
