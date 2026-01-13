"""
Swagger 导入和 Debug 执行端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import os
import json
import yaml
import subprocess
from app.core.deps import get_db
from app.models.api_info import ApiInfo
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select

router = APIRouter(prefix="/ApiInfo", tags=["Swagger导入和Debug执行"])


@router.post("/debug", response_model=respModel)
async def debug_execute(
    *,
    id: int = Query(..., ge=1, description='API信息ID'),
    download_response: Optional[bool] = Query(False, description='是否下载响应'),
    db: AsyncSession = Depends(get_db)
):
    """调试执行接口"""
    try:
        # 获取对应的测试用例信息
        result = await db.execute(select(ApiInfo).where(ApiInfo.id == id))
        api_info = result.scalars().first()
        if not api_info:
            raise NotFoundException("API信息不存在")
        
        # 创建执行目录，用来存放测试用例和配置文件
        cases_dir = os.path.join(os.getcwd(), "test_cases")  # 可配置路径
        execute_uuid = str(uuid.uuid4())
        run_tmp_dir = os.path.join(cases_dir, execute_uuid)
        os.makedirs(run_tmp_dir, exist_ok=True)
        
        # 获取 Debug变量 数据，生成 context.yaml 文件
        context_data = {}
        context_yaml_file = os.path.join(run_tmp_dir, "context.yaml")
        
        if api_info.debug_vars and api_info.debug_vars != "null":
            try:
                context_data = json.loads(api_info.debug_vars)
            except json.JSONDecodeError:
                context_data = {}
        
        with open(context_yaml_file, "w", encoding="utf-8") as context_file:
            yaml.dump(context_data, context_file, default_flow_style=False, encoding='utf-8', allow_unicode=True)
        
        # 填充测试用例信息
        steps_info = {}
        test_case_data = {
            "desc": api_info.api_name,
            "steps": [
                {
                    api_info.api_name: steps_info
                }
            ]
        }
        
        if download_response:
            steps_info.update({
                "关键字": "send_request_and_download",
                "method": api_info.request_method,
                "url": api_info.request_url
            })
        else:
            steps_info.update({
                "关键字": "send_request",
                "method": api_info.request_method,
                "url": api_info.request_url
            })
        
        # 添加请求参数
        if api_info.request_params:
            steps_info["params"] = api_info.request_params
        
        if api_info.request_headers:
            try:
                steps_info["headers"] = json.loads(api_info.request_headers)
            except json.JSONDecodeError:
                steps_info["headers"] = api_info.request_headers
        
        if api_info.requests_json_data:
            steps_info["json"] = api_info.requests_json_data
        
        # 保存测试用例文件
        test_case_file = os.path.join(run_tmp_dir, "test_case.yaml")
        with open(test_case_file, "w", encoding="utf-8") as f:
            yaml.dump(test_case_data, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
        
        # 执行测试用例（这里可以集成实际的测试执行器）
        execution_result = {
            "execute_uuid": execute_uuid,
            "test_case_file": test_case_file,
            "context_file": context_yaml_file,
            "status": "created",
            "message": "测试用例创建成功，等待执行"
        }
        
        return respModel().ok_resp(obj=execution_result, msg="调试执行创建成功")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调试执行失败: {str(e)}")


@router.post("/swagger_import", response_model=respModel)
async def swagger_import(
    *,
    file: UploadFile = File(..., description='Swagger JSON/YAML文件'),
    project_id: Optional[int] = Query(None, description='项目ID'),
    db: AsyncSession = Depends(get_db)
):
    """Swagger 文档导入"""
    try:
        # 读取上传的文件内容
        content = await file.read()
        
        # 解析 Swagger 文档
        try:
            swagger_data = yaml.safe_load(content)
        except yaml.YAMLError:
            # 如果不是 YAML，尝试 JSON
            swagger_data = json.loads(content.decode('utf-8'))
        
        # 提取 API 信息
        imported_count = 0
        if 'paths' in swagger_data:
            for path, methods in swagger_data['paths'].items():
                for method, details in methods.items():
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                        # 创建 API 信息记录
                        api_info = ApiInfo(
                            project_id=project_id,
                            api_name=details.get('summary', f"{method.upper()} {path}"),
                            request_method=method.upper(),
                            request_url=path,
                            request_params=json.dumps(details.get('parameters', [])),
                            request_headers=json.dumps(details.get('responses', {})),
                            debug_vars=json.dumps({})
                        )
                        
                        db.add(api_info)
                        imported_count += 1
            
            await db.commit()
        
        return respModel().ok_resp(
            dic_t={"imported_count": imported_count}, 
            msg=f"成功导入 {imported_count} 个 API 接口"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Swagger 导入失败: {str(e)}")
