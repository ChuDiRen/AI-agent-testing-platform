"""
API测试报告查看器Controller
提供公共访问的测试报告查看功能,无需认证
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from sqlmodel import Session, select
from pathlib import Path
from typing import Optional
import os
import json

from core.resp_model import respModel
from core.logger import get_logger
from core.database import get_session
from ..model.ApiHistoryModel import ApiHistory

logger = get_logger(__name__)

# 配置常量
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
REPORT_DIR = TEMP_DIR / "allure_reports"

module_name = "ApiReportViewer"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试报告查看"])


@module_route.get("/view")
async def view_report(
    history_id: Optional[int] = Query(None, description="测试历史记录ID"),
    execution_uuid: Optional[str] = Query(None, description="批量执行UUID"),
    report_path: Optional[str] = Query(None, description="报告路径")
):
    """
    查看测试报告（公共端点,无需认证）
    
    支持三种方式访问:
    1. 通过 history_id 查看单个测试的报告
    2. 通过 execution_uuid 查看批量执行的报告
    3. 直接通过 report_path 访问报告
    
    Args:
        history_id: 测试历史记录ID
        execution_uuid: 批量执行UUID
        report_path: 报告路径（相对于REPORT_DIR）
    
    Returns:
        HTML: Allure报告的index.html页面
    """
    try:
        target_report_path = None
        
        # 方式1: 通过 history_id 查找
        if history_id:
            from core.database import get_session
            with next(get_session()) as session:
                history = session.get(ApiHistory, history_id)
                if history and history.allure_report_path:
                    target_report_path = Path(history.allure_report_path)
                    logger.info(f"通过history_id={history_id}查找报告: {target_report_path}")
        
        # 方式2: 通过 execution_uuid 查找
        elif execution_uuid:
            from core.database import get_session
            with next(get_session()) as session:
                statement = select(ApiHistory).where(
                    ApiHistory.execution_uuid == execution_uuid
                ).limit(1)
                history = session.exec(statement).first()
                if history and history.allure_report_path:
                    target_report_path = Path(history.allure_report_path)
                    logger.info(f"通过execution_uuid={execution_uuid}查找报告: {target_report_path}")
        
        # 方式3: 直接通过 report_path 访问
        elif report_path:
            # 安全检查: 防止路径遍历攻击
            safe_path = Path(report_path).resolve()
            if not str(safe_path).startswith(str(REPORT_DIR.resolve())):
                raise HTTPException(status_code=403, detail="非法的报告路径")
            target_report_path = safe_path
            logger.info(f"直接访问报告路径: {target_report_path}")
        
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "msg": "请提供 history_id、execution_uuid 或 report_path 参数之一",
                    "data": None
                }
            )
        
        # 检查报告是否存在
        if not target_report_path or not target_report_path.exists():
            logger.warning(f"报告不存在: {target_report_path}")
            return HTMLResponse(
                content=generate_not_found_html(),
                status_code=404
            )
        
        # 查找 index.html
        index_file = target_report_path / "index.html"
        if not index_file.exists():
            logger.warning(f"报告index.html不存在: {index_file}")
            return HTMLResponse(
                content=generate_not_found_html("报告文件不完整"),
                status_code=404
            )
        
        # 返回报告页面
        logger.info(f"成功访问报告: {index_file}")
        return FileResponse(
            path=str(index_file),
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache",
                "X-Report-Path": str(target_report_path.relative_to(REPORT_DIR))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查看报告失败: {e}", exc_info=True)
        return HTMLResponse(
            content=generate_error_html(str(e)),
            status_code=500
        )


@module_route.get("/download")
async def download_report(
    history_id: Optional[int] = Query(None, description="测试历史记录ID"),
    execution_uuid: Optional[str] = Query(None, description="批量执行UUID")
):
    """
    下载测试报告压缩包
    
    Args:
        history_id: 测试历史记录ID
        execution_uuid: 批量执行UUID
    
    Returns:
        ZIP文件: 报告压缩包
    """
    try:
        import zipfile
        import tempfile
        from datetime import datetime
        
        target_report_path = None
        report_name = "report"
        
        # 通过 history_id 查找
        if history_id:
            from core.database import get_session
            with next(get_session()) as session:
                history = session.get(ApiHistory, history_id)
                if history and history.allure_report_path:
                    target_report_path = Path(history.allure_report_path)
                    report_name = f"report_{history.test_name}_{history_id}"
        
        # 通过 execution_uuid 查找
        elif execution_uuid:
            from core.database import get_session
            with next(get_session()) as session:
                statement = select(ApiHistory).where(
                    ApiHistory.execution_uuid == execution_uuid
                ).limit(1)
                history = session.exec(statement).first()
                if history and history.allure_report_path:
                    target_report_path = Path(history.allure_report_path)
                    report_name = f"report_{execution_uuid}"
        
        else:
            raise HTTPException(status_code=400, detail="请提供 history_id 或 execution_uuid 参数")
        
        # 检查报告是否存在
        if not target_report_path or not target_report_path.exists():
            raise HTTPException(status_code=404, detail="报告不存在")
        
        # 创建临时ZIP文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{report_name}_{timestamp}.zip"
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        try:
            # 压缩报告目录
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in target_report_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(target_report_path)
                        zipf.write(file_path, arcname)
            
            logger.info(f"成功创建报告压缩包: {zip_filename}")
            
            # 返回ZIP文件
            return FileResponse(
                path=temp_zip.name,
                media_type="application/zip",
                filename=zip_filename,
                headers={
                    "Content-Disposition": f"attachment; filename={zip_filename}"
                }
            )
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_zip.name):
                os.unlink(temp_zip.name)
            raise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")


@module_route.get("/list")
async def list_reports():
    """
    列出所有可用的测试报告
    
    Returns:
        JSON: 报告列表
    """
    try:
        from core.database import get_session
        
        with next(get_session()) as session:
            # 查询最近100条有报告的测试记录
            statement = select(ApiHistory).where(
                ApiHistory.allure_report_path.isnot(None)
            ).order_by(ApiHistory.create_time.desc()).limit(100)
            
            histories = session.exec(statement).all()
            
            result_list = []
            for history in histories:
                # 检查报告是否仍然存在
                report_path = Path(history.allure_report_path)
                exists = report_path.exists() if history.allure_report_path else False
                
                item = {
                    "id": history.id,
                    "test_name": history.test_name,
                    "test_status": history.test_status,
                    "execution_uuid": history.execution_uuid,
                    "project_id": history.project_id,
                    "plan_id": history.plan_id,
                    "case_info_id": history.case_info_id,
                    "report_exists": exists,
                    "report_path": str(report_path.relative_to(REPORT_DIR)) if exists else None,
                    "create_time": history.create_time.isoformat() if history.create_time else None,
                    "finish_time": history.finish_time.isoformat() if history.finish_time else None,
                    "view_url": f"/ApiReportViewer/view?history_id={history.id}",
                    "download_url": f"/ApiReportViewer/download?history_id={history.id}"
                }
                result_list.append(item)
            
            return {
                "code": 200,
                "msg": "查询成功",
                "data": {
                    "list": result_list,
                    "total": len(result_list)
                }
            }
        
    except Exception as e:
        logger.error(f"列出报告失败: {e}", exc_info=True)
        return {
            "code": 500,
            "msg": f"服务器错误: {str(e)}",
            "data": None
        }


def generate_not_found_html(message: str = "报告不存在") -> str:
    """生成404页面HTML"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>报告不存在</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                text-align: center;
                background: white;
                padding: 60px 80px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            h1 {{
                font-size: 72px;
                margin: 0;
                color: #667eea;
            }}
            p {{
                font-size: 24px;
                color: #666;
                margin: 20px 0;
            }}
            .message {{
                font-size: 18px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>404</h1>
            <p>{message}</p>
            <p class="message">请检查报告ID或路径是否正确</p>
        </div>
    </body>
    </html>
    """


def generate_error_html(error: str) -> str:
    """生成错误页面HTML"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>服务器错误</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            .container {{
                text-align: center;
                background: white;
                padding: 60px 80px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
            }}
            h1 {{
                font-size: 72px;
                margin: 0;
                color: #f5576c;
            }}
            p {{
                font-size: 24px;
                color: #666;
                margin: 20px 0;
            }}
            .error {{
                font-size: 14px;
                color: #999;
                background: #f5f5f5;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>500</h1>
            <p>服务器错误</p>
            <div class="error">{error}</div>
        </div>
    </body>
    </html>
    """
