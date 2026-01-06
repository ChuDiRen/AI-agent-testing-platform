"""
Web测试报告Controller - 按照ApiTest标准实现
"""
import json
import os
from typing import List
from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import FileResponse
from sqlmodel import Session

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel

from ..service.WebReportService import WebReportService
from ..schemas.WebReportSchema import (
    WebReportQuery, WebReportCreate, WebReportUpdate, 
    WebReportResponse, WebReportGenerateRequest, WebReportDownloadRequest,
    WebReportStatistics, BatchDeleteRequest
)

module_name = "WebReport"
module_route = APIRouter(prefix=f"/{module_name}", tags=["Web测试报告"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询报告", dependencies=[Depends(check_permission("webtest:report:query"))])
async def queryByPage(query: WebReportQuery, session: Session = Depends(get_session)):
    """分页查询报告"""
    try:
        reports, total = WebReportService.query_by_page(session, query)
        
        # 转换为响应格式
        report_responses = []
        for report in reports:
            report_dict = report.dict()
            
            # 解析JSON字段
            if report.summary_data:
                try:
                    report_dict['summary_data'] = json.loads(report.summary_data)
                except json.JSONDecodeError:
                    report_dict['summary_data'] = {}
            else:
                report_dict['summary_data'] = {}
            
            if report.detail_data:
                try:
                    report_dict['detail_data'] = json.loads(report.detail_data)
                except json.JSONDecodeError:
                    report_dict['detail_data'] = {}
            else:
                report_dict['detail_data'] = {}
            
            if report.chart_data:
                try:
                    report_dict['chart_data'] = json.loads(report.chart_data)
                except json.JSONDecodeError:
                    report_dict['chart_data'] = {}
            else:
                report_dict['chart_data'] = {}
            
            report_responses.append(report_dict)
        
        return respModel.ok_resp_list(lst=report_responses, total=total)
    except Exception as e:
        logger.error(f"分页查询报告失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryById", summary="查询报告详情", dependencies=[Depends(check_permission("webtest:report:query"))])
async def queryById(id: str = Query(..., description="报告ID"), session: Session = Depends(get_session)):
    """查询报告详情"""
    try:
        report = WebReportService.query_by_id(session, id)
        if not report:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 转换为响应格式
        report_dict = report.dict()
        
        # 解析JSON字段
        if report.summary_data:
            try:
                report_dict['summary_data'] = json.loads(report.summary_data)
            except json.JSONDecodeError:
                report_dict['summary_data'] = {}
        else:
            report_dict['summary_data'] = {}
        
        if report.detail_data:
            try:
                report_dict['detail_data'] = json.loads(report.detail_data)
            except json.JSONDecodeError:
                report_dict['detail_data'] = {}
        else:
            report_dict['detail_data'] = {}
        
        if report.chart_data:
            try:
                report_dict['chart_data'] = json.loads(report.chart_data)
            except json.JSONDecodeError:
                report_dict['chart_data'] = {}
        else:
            report_dict['chart_data'] = {}
        
        return respModel.ok_resp(obj=report_dict)
    except Exception as e:
        logger.error(f"查询报告详情失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/generate", summary="生成报告", dependencies=[Depends(check_permission("webtest:report:add"))])
async def generate(request: WebReportGenerateRequest, session: Session = Depends(get_session)):
    """生成报告"""
    try:
        report = WebReportService.generate_report(session, request)
        return respModel.ok_resp(msg="报告生成成功", dic_t={"id": report.id})
    except Exception as e:
        logger.error(f"生成报告失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"生成失败:{e}")


@module_route.post("/insert", summary="新增报告", dependencies=[Depends(check_permission("webtest:report:add"))])
async def insert(report_data: WebReportCreate, session: Session = Depends(get_session)):
    """新增报告"""
    try:
        report = WebReportService.create(session, report_data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": report.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增报告失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新报告", dependencies=[Depends(check_permission("webtest:report:edit"))])
async def update(report_data: WebReportUpdate, session: Session = Depends(get_session)):
    """更新报告"""
    try:
        success = WebReportService.update(session, report_data.id, report_data)
        if success:
            return respModel.ok_resp(msg="更新成功")
        else:
            return respModel.error_resp("报告不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新报告失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除报告", dependencies=[Depends(check_permission("webtest:report:delete"))])
async def delete(id: str = Query(..., description="报告ID"), session: Session = Depends(get_session)):
    """删除报告"""
    try:
        success = WebReportService.delete(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("报告不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除报告失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.delete("/batchDelete", summary="批量删除报告", dependencies=[Depends(check_permission("webtest:report:delete"))])
async def batchDelete(request: BatchDeleteRequest, session: Session = Depends(get_session)):
    """批量删除报告"""
    try:
        deleted_count = WebReportService.batch_delete(session, request.ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}条报告")
        else:
            return respModel.error_resp("没有找到要删除的报告")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除报告失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量删除失败：{e}")


@module_route.get("/getStatistics", summary="获取报告统计", dependencies=[Depends(check_permission("webtest:report:query"))])
async def getStatistics(
    project_id: int = Query(None, description="项目ID"),
    days: int = Query(default=30, description="统计天数"),
    session: Session = Depends(get_session)
):
    """获取报告统计信息"""
    try:
        stats = WebReportService.get_statistics(session, project_id, days)
        return respModel.ok_resp(obj=stats.dict())
    except Exception as e:
        logger.error(f"获取报告统计失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/download/{report_id}", summary="下载报告", dependencies=[Depends(check_permission("webtest:report:download"))])
async def download(
    report_id: str = Path(..., description="报告ID"),
    format: str = Query(default="html", description="下载格式"),
    session: Session = Depends(get_session)
):
    """下载报告文件"""
    try:
        report = WebReportService.query_by_id(session, report_id)
        if not report or report.status != "completed":
            return respModel.error_resp("报告不存在或未生成完成")
        
        # 检查文件是否存在
        if not report.file_path or not os.path.exists(report.file_path):
            return respModel.error_resp("报告文件不存在")
        
        # 返回文件
        return FileResponse(
            path=report.file_path,
            filename=f"{report.report_name}.{format}",
            media_type="application/octet-stream"
        )
    except Exception as e:
        logger.error(f"下载报告失败: {e}", exc_info=True)
        return respModel.error_resp(f"下载失败：{e}")


@module_route.get("/view/{report_id}", summary="查看报告", dependencies=[Depends(check_permission("webtest:report:view"))])
async def view(report_id: str = Path(..., description="报告ID"), session: Session = Depends(get_session)):
    """查看报告内容"""
    try:
        report = WebReportService.query_by_id(session, report_id)
        if not report or report.status != "completed":
            return respModel.error_resp("报告不存在或未生成完成")
        
        # 检查文件是否存在
        if not report.file_path or not os.path.exists(report.file_path):
            return respModel.error_resp("报告文件不存在")
        
        # 返回HTML内容
        with open(report.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return respModel.ok_resp(obj={"content": content, "format": report.format})
    except Exception as e:
        logger.error(f"查看报告失败: {e}", exc_info=True)
        return respModel.error_resp(f"查看失败：{e}")


@module_route.get("/allure/{execution_id}", summary="获取Allure报告链接", dependencies=[Depends(check_permission("webtest:report:view"))])
async def getAllureUrl(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """获取Allure报告链接"""
    try:
        # 查找对应的报告
        from ..service.WebHistoryService import WebHistoryService
        history = WebHistoryService.query_by_id(session, execution_id)
        if not history:
            return respModel.error_resp("执行记录不存在")
        
        # 构建Allure报告URL
        allure_url = f"/allure-report/{execution_id}/index.html"
        
        # 如果有自定义的Allure路径，使用自定义路径
        if history.allure_path:
            allure_url = history.allure_path
        
        return respModel.ok_resp(obj={"url": allure_url})
    except Exception as e:
        logger.error(f"获取Allure报告链接失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败：{e}")


@module_route.get("/getReportData/{execution_id}", summary="获取报告数据", dependencies=[Depends(check_permission("webtest:report:query"))])
async def getReportData(
    execution_id: str = Path(..., description="执行ID"),
    session: Session = Depends(get_session)
):
    """获取报告数据（供前端使用）"""
    try:
        # 查找对应的报告
        report = WebReportService.query_by_execution_id(session, execution_id)
        if not report:
            # 如果没有报告，尝试从执行历史生成数据
            from ..service.WebHistoryService import WebHistoryService
            history = WebHistoryService.query_by_id(session, execution_id)
            if not history:
                return respModel.error_resp("执行记录不存在")
            
            # 构建基础数据
            report_data = {
                "id": history.id,
                "project_name": history.project_name,
                "start_time": history.start_time.isoformat(),
                "duration": history.duration,
                "executor": history.executor,
                "total": history.total,
                "passed": history.passed,
                "failed": history.failed,
                "skipped": 0,
                "pass_rate": history.pass_rate,
                "env": history.env,
                "browsers": json.loads(history.browsers) if history.browsers else [],
                "threads": history.threads,
                "cases": []
            }
            
            # 获取用例详情
            cases = WebHistoryService.query_cases_by_execution(session, execution_id)
            for case in cases:
                case_data = {
                    "name": case.case_name,
                    "status": case.status,
                    "duration": case.duration,
                    "browser": "chromium",
                    "screenshot": bool(case.screenshot_path),
                    "error": case.error_message,
                    "steps": json.loads(case.step_results) if case.step_results else []
                }
                report_data["cases"].append(case_data)
            
            return respModel.ok_resp(obj=report_data)
        
        # 解析报告数据
        report_dict = report.dict()
        
        if report.summary_data:
            try:
                summary_data = json.loads(report.summary_data)
            except json.JSONDecodeError:
                summary_data = {}
        else:
            summary_data = {}
        
        if report.detail_data:
            try:
                detail_data = json.loads(report.detail_data)
            except json.JSONDecodeError:
                detail_data = {"cases": []}
        else:
            detail_data = {"cases": []}
        
        # 合并数据
        report_data = {**summary_data, **detail_data}
        
        return respModel.ok_resp(obj=report_data)
    except Exception as e:
        logger.error(f"获取报告数据失败: {e}", exc_info=True)
        return respModel.error_resp(f"获取失败：{e}")
