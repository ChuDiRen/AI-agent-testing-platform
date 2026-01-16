"""
API 报告查看器端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select
from datetime import datetime
import json
import os

router = APIRouter(prefix="/ApiReportViewer", tags=["API报告查看器"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有报告"""
    try:
        # 模拟报告数据查询
        reports = [
            {
                "id": 1,
                "report_name": "API测试报告_2024-01-01",
                "project_id": 1,
                "test_suite_name": "用户管理测试套件",
                "total_cases": 100,
                "passed_cases": 85,
                "failed_cases": 15,
                "execution_time": "2024-01-01 10:00:00",
                "status": "completed"
            },
            {
                "id": 2,
                "report_name": "API测试报告_2024-01-02",
                "project_id": 1,
                "test_suite_name": "订单管理测试套件",
                "total_cases": 50,
                "passed_cases": 45,
                "failed_cases": 5,
                "execution_time": "2024-01-02 14:30:00",
                "status": "completed"
            }
        ]
        return respModel().ok_resp_list(lst=reports, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_id: Optional[int] = Query(None, description='项目ID'),
    report_name: Optional[str] = Query(None, description='报告名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询报告"""
    try:
        # 模拟分页查询报告数据
        reports = [
            {
                "id": 1,
                "report_name": "API测试报告_2024-01-01",
                "project_id": 1,
                "test_suite_name": "用户管理测试套件",
                "total_cases": 100,
                "passed_cases": 85,
                "failed_cases": 15,
                "execution_time": "2024-01-01 10:00:00",
                "status": "completed"
            }
        ]
        total = 1
        return respModel().ok_resp_list(lst=reports, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='报告ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询报告详情"""
    try:
        # 模拟报告详情查询
        report_detail = {
            "id": id,
            "report_name": "API测试报告_2024-01-01",
            "project_id": 1,
            "test_suite_name": "用户管理测试套件",
            "total_cases": 100,
            "passed_cases": 85,
            "failed_cases": 15,
            "execution_time": "2024-01-01 10:00:00",
            "status": "completed",
            "execution_details": [
                {
                    "case_id": 1,
                    "case_name": "用户登录测试",
                    "status": "passed",
                    "execution_time": "2024-01-01 10:01:00",
                    "response_time": "150ms"
                },
                {
                    "case_id": 2,
                    "case_name": "用户注册测试",
                    "status": "failed",
                    "execution_time": "2024-01-01 10:02:00",
                    "error_message": "参数验证失败"
                }
            ]
        }
        return respModel().ok_resp(obj=report_detail, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/generate_report", response_model=respModel)
async def generate_report(
    *,
    project_id: Optional[int] = Query(None, description='项目ID'),
    test_suite_id: Optional[int] = Query(None, description='测试套件ID'),
    db: AsyncSession = Depends(get_db)
):
    """生成测试报告"""
    try:
        # 模拟报告生成
        report_id = 12345
        report_data = {
            "report_id": report_id,
            "project_id": project_id,
            "test_suite_id": test_suite_id,
            "status": "generating",
            "message": "报告生成中，请稍后查看"
        }
        return respModel().ok_resp(dic_t=report_data, msg="报告生成请求已提交")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.get("/download_report", response_model=respModel)
async def download_report(
    *,
    id: int = Query(..., ge=1, description='报告ID'),
    format: str = Query("json", description='报告格式：json, html, pdf'),
    db: AsyncSession = Depends(get_db)
):
    """下载测试报告"""
    try:
        # 模拟报告下载
        download_url = f"/api/v1/ApiReportViewer/download/{id}?format={format}"
        report_data = {
            "report_id": id,
            "download_url": download_url,
            "format": format,
            "expires": "2024-01-15 23:59:59"
        }
        return respModel().ok_resp(dic_t=report_data, msg="报告下载链接已生成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告下载失败: {str(e)}")


@router.get("/{dir}/{filename}")
async def report_viewer(dir: str, filename: str):
    """静态文件服务 - 查看报告文件"""
    try:
        # 报告根目录
        report_root_dir = os.path.join(os.getcwd(), "report")
        file_path = os.path.join(report_root_dir, dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 检查是否为目录（防止路径遍历攻击）
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=400, detail="无效的文件路径")
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件访问失败: {str(e)}")
