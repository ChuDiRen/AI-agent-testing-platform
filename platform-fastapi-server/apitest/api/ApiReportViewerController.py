"""
API测试报告查看器Controller
提供公共访问的测试报告查看功能,无需认证
"""
import os
from pathlib import Path
from typing import Optional

from core.database import get_session
from core.logger import get_logger
from core.resp_model import respModel
from core.temp_manager import get_temp_subdir
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from sqlmodel import select

from ..model.ApiHistoryModel import ApiHistory

logger = get_logger(__name__)

# 配置常量
# ✅ P2修复: 使用配置管理的路径,避免硬编码
from config.dev_settings import settings

BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
REPORT_DIR = settings.REPORT_DIR

module_name = "ApiReportViewer"
module_route = APIRouter(prefix=f"/{module_name}", tags=["API测试报告查看"])


def find_report_file(target_report_path: Path) -> Optional[Path]:
    """
    智能查找报告文件
    
    查找顺序：
    1. 目标目录下的 complete.html
    2. 目标目录下的 index.html
    3. 关联的 venv/site-packages/reports/complete.html（执行器生成的报告）
    
    Args:
        target_report_path: 测试执行目录路径
    
    Returns:
        报告文件路径，未找到返回 None
    """
    if not target_report_path:
        return None
    
    # 1. 目标目录下的 complete.html
    if target_report_path.exists():
        complete_file = target_report_path / "complete.html"
        if complete_file.exists():
            return complete_file
        
        # 2. 目标目录下的 index.html
        index_file = target_report_path / "index.html"
        if index_file.exists():
            return index_file
    
    # 3. 查找关联的执行器 venv 中的报告
    # 路径格式: temp/executor/case_xxx -> 查找 temp/executor/plugin_xxx/venv/.../reports/complete.html
    try:
        # 从测试目录名提取信息，查找对应的插件目录
        # 测试目录格式: case_{case_id}_{timestamp}_{uuid}
        executor_base = target_report_path.parent  # temp/executor
        
        # 遍历所有 plugin_* 目录
        if executor_base.exists():
            for plugin_dir in executor_base.iterdir():
                if plugin_dir.is_dir() and plugin_dir.name.startswith("plugin_"):
                    # 查找 venv/Lib/site-packages/reports/complete.html (Windows)
                    venv_report = plugin_dir / "venv" / "Lib" / "site-packages" / "reports" / "complete.html"
                    if venv_report.exists():
                        logger.info(f"在 venv 中找到报告: {venv_report}")
                        return venv_report
                    
                    # 查找 venv/lib/python*/site-packages/reports/complete.html (Linux)
                    venv_lib = plugin_dir / "venv" / "lib"
                    if venv_lib.exists():
                        for py_dir in venv_lib.iterdir():
                            if py_dir.name.startswith("python"):
                                venv_report = py_dir / "site-packages" / "reports" / "complete.html"
                                if venv_report.exists():
                                    logger.info(f"在 venv 中找到报告: {venv_report}")
                                    return venv_report
    except Exception as e:
        logger.warning(f"查找 venv 报告失败: {e}")
    
    return None


@module_route.get("/view", summary="查看测试报告")
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
                    # 处理相对路径和绝对路径
                    report_path = Path(history.allure_report_path)
                    if not report_path.is_absolute():
                        target_report_path = BASE_DIR / report_path
                    else:
                        target_report_path = report_path
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
                    # 处理相对路径和绝对路径
                    report_path = Path(history.allure_report_path)
                    if not report_path.is_absolute():
                        target_report_path = BASE_DIR / report_path
                    else:
                        target_report_path = report_path
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
        
        # 查找报告文件（支持多种位置和格式）
        report_file = find_report_file(target_report_path)
        
        if report_file and report_file.exists():
            logger.info(f"找到报告文件: {report_file}")
            return FileResponse(
                path=str(report_file),
                media_type="text/html",
                headers={"Cache-Control": "no-cache"}
            )
        
        # 尝试查找执行结果文件（非 Allure 报告）
        if target_report_path and target_report_path.exists():
            result_file = target_report_path / "result.json"
            stdout_file = target_report_path / "stdout.log"
            
            if result_file.exists() or stdout_file.exists():
                # 生成简单的执行结果页面
                logger.info(f"生成执行结果页面: {target_report_path}")
                return HTMLResponse(
                    content=generate_execution_result_html(target_report_path),
                    status_code=200
                )
        
        logger.warning(f"报告文件不存在: {target_report_path}")
        return HTMLResponse(
            content=generate_not_found_html("报告文件不存在"),
            status_code=404
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查看报告失败: {e}", exc_info=True)
        return HTMLResponse(
            content=generate_error_html(str(e)),
            status_code=500
        )


@module_route.get("/download", summary="下载测试报告")
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
        
        # 创建临时ZIP文件（使用项目 temp 目录）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{report_name}_{timestamp}.zip"
        temp_zip_path = get_temp_subdir("reports") / zip_filename
        
        try:
            # 压缩报告目录
            with zipfile.ZipFile(str(temp_zip_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in target_report_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(target_report_path)
                        zipf.write(file_path, arcname)
            
            logger.info(f"成功创建报告压缩包: {zip_filename}")
            
            # 返回ZIP文件
            return FileResponse(
                path=str(temp_zip_path),
                media_type="application/zip",
                filename=zip_filename,
                headers={
                    "Content-Disposition": f"attachment; filename={zip_filename}"
                }
            )
        except Exception as e:
            # 清理临时文件
            if temp_zip_path.exists():
                temp_zip_path.unlink()
            raise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")


@module_route.get("/list", summary="列出所有测试报告")
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


def generate_execution_result_html(report_path: Path) -> str:
    """生成执行结果页面HTML"""
    import json
    
    result_content = ""
    stdout_content = ""
    stderr_content = ""
    
    # 读取 result.json
    result_file = report_path / "result.json"
    if result_file.exists():
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
                result_content = json.dumps(result_data, indent=2, ensure_ascii=False)
        except Exception as e:
            result_content = f"读取失败: {e}"
    
    # 读取 stdout.log
    stdout_file = report_path / "stdout.log"
    if stdout_file.exists():
        try:
            with open(stdout_file, 'r', encoding='utf-8') as f:
                stdout_content = f.read()
        except Exception as e:
            stdout_content = f"读取失败: {e}"
    
    # 读取 stderr.log
    stderr_file = report_path / "stderr.log"
    if stderr_file.exists():
        try:
            with open(stderr_file, 'r', encoding='utf-8') as f:
                stderr_content = f.read()
        except Exception as e:
            stderr_content = f"读取失败: {e}"
    
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>执行结果</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                color: #333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }}
            .section {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #667eea;
                margin-bottom: 15px;
                font-size: 18px;
            }}
            pre {{
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 15px;
                border-radius: 6px;
                overflow-x: auto;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.5;
                max-height: 400px;
                overflow-y: auto;
            }}
            .empty {{
                color: #999;
                font-style: italic;
            }}
            .error {{
                color: #f56c6c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📋 执行结果</h1>
            
            <div class="section">
                <h2>📊 测试结果 (result.json)</h2>
                {f'<pre>{result_content}</pre>' if result_content else '<p class="empty">无结果数据</p>'}
            </div>
            
            <div class="section">
                <h2>📝 标准输出 (stdout.log)</h2>
                {f'<pre>{stdout_content}</pre>' if stdout_content else '<p class="empty">无输出</p>'}
            </div>
            
            <div class="section">
                <h2>⚠️ 错误输出 (stderr.log)</h2>
                {f'<pre class="error">{stderr_content}</pre>' if stderr_content else '<p class="empty">无错误</p>'}
            </div>
        </div>
    </body>
    </html>
    """


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
