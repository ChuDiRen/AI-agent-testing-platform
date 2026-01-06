"""
Web测试执行历史Controller - 按照ApiTest标准实现
"""
import json
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel

from ..service.WebHistoryService import WebHistoryService
from ..schemas.WebHistorySchema import (
    WebHistoryQuery, WebHistoryCreate, WebHistoryUpdate, 
    WebHistoryResponse, WebHistoryCaseResponse, BatchDeleteRequest
)

module_name = "WebHistory"
module_route = APIRouter(prefix=f"/{module_name}", tags=["Web执行历史"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询执行历史", dependencies=[Depends(check_permission("webtest:history:query"))])
async def queryByPage(query: WebHistoryQuery, session: Session = Depends(get_session)):
    """分页查询执行历史"""
    try:
        histories, total = WebHistoryService.query_by_page(session, query)
        
        # 转换为响应格式
        history_responses = []
        for history in histories:
            history_dict = history.dict()
            
            # 解析JSON字段
            if history.browsers:
                try:
                    history_dict['browsers'] = json.loads(history.browsers)
                except json.JSONDecodeError:
                    history_dict['browsers'] = []
            else:
                history_dict['browsers'] = []
            
            if history.case_ids:
                try:
                    history_dict['case_ids'] = json.loads(history.case_ids)
                except json.JSONDecodeError:
                    history_dict['case_ids'] = []
            else:
                history_dict['case_ids'] = []
            
            history_responses.append(history_dict)
        
        return respModel.ok_resp_list(lst=history_responses, total=total)
    except Exception as e:
        logger.error(f"分页查询执行历史失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryById", summary="查询执行详情", dependencies=[Depends(check_permission("webtest:history:query"))])
async def queryById(id: str = Query(..., description="执行ID"), session: Session = Depends(get_session)):
    """查询执行详情"""
    try:
        history = WebHistoryService.query_by_id(session, id)
        if not history:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 转换为响应格式
        history_dict = history.dict()
        
        # 解析JSON字段
        if history.browsers:
            try:
                history_dict['browsers'] = json.loads(history.browsers)
            except json.JSONDecodeError:
                history_dict['browsers'] = []
        else:
            history_dict['browsers'] = []
        
        if history.case_ids:
            try:
                history_dict['case_ids'] = json.loads(history.case_ids)
            except json.JSONDecodeError:
                history_dict['case_ids'] = []
        else:
            history_dict['case_ids'] = []
        
        # 查询用例详情
        cases = WebHistoryService.query_cases_by_execution(session, id)
        case_responses = []
        for case in cases:
            case_dict = case.dict()
            if case.step_results:
                try:
                    case_dict['step_results'] = json.loads(case.step_results)
                except json.JSONDecodeError:
                    case_dict['step_results'] = []
            else:
                case_dict['step_results'] = []
            case_responses.append(case_dict)
        
        history_dict['cases'] = case_responses
        
        return respModel.ok_resp(obj=history_dict)
    except Exception as e:
        logger.error(f"查询执行详情失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/insert", summary="新增执行历史", dependencies=[Depends(check_permission("webtest:history:add"))])
async def insert(history_data: WebHistoryCreate, session: Session = Depends(get_session)):
    """新增执行历史"""
    try:
        history = WebHistoryService.create(session, history_data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": history.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增执行历史失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新执行历史", dependencies=[Depends(check_permission("webtest:history:edit"))])
async def update(history_data: WebHistoryUpdate, session: Session = Depends(get_session)):
    """更新执行历史"""
    try:
        success = WebHistoryService.update(session, history_data.id, history_data)
        if success:
            return respModel.ok_resp(msg="更新成功")
        else:
            return respModel.error_resp("执行记录不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新执行历史失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除执行历史", dependencies=[Depends(check_permission("webtest:history:delete"))])
async def delete(id: str = Query(..., description="执行ID"), session: Session = Depends(get_session)):
    """删除执行历史"""
    try:
        success = WebHistoryService.delete(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("执行记录不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除执行历史失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.delete("/batchDelete", summary="批量删除执行历史", dependencies=[Depends(check_permission("webtest:history:delete"))])
async def batchDelete(request: BatchDeleteRequest, session: Session = Depends(get_session)):
    """批量删除执行历史"""
    try:
        deleted_count = WebHistoryService.batch_delete(session, request.ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}条记录")
        else:
            return respModel.error_resp("没有找到要删除的记录")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除执行历史失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量删除失败：{e}")


@module_route.get("/getStatistics", summary="获取执行统计", dependencies=[Depends(check_permission("webtest:history:query"))])
async def getStatistics(
    project_id: int = Query(None, description="项目ID"),
    days: int = Query(default=7, description="统计天数"),
    session: Session = Depends(get_session)
):
    """获取执行统计信息"""
    try:
        stats = WebHistoryService.get_statistics(session, project_id, days)
        return respModel.ok_resp(obj=stats)
    except Exception as e:
        logger.error(f"获取执行统计失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryCases", summary="查询执行用例详情", dependencies=[Depends(check_permission("webtest:history:query"))])
async def queryCases(
    execution_id: str = Query(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """查询执行用例详情"""
    try:
        cases = WebHistoryService.query_cases_by_execution(session, execution_id)
        
        # 转换为响应格式
        case_responses = []
        for case in cases:
            case_dict = case.dict()
            if case.step_results:
                try:
                    case_dict['step_results'] = json.loads(case.step_results)
                except json.JSONDecodeError:
                    case_dict['step_results'] = []
            else:
                case_dict['step_results'] = []
            case_responses.append(case_dict)
        
        return respModel.ok_resp_list(lst=case_responses, total=len(case_responses))
    except Exception as e:
        logger.error(f"查询执行用例详情失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")
