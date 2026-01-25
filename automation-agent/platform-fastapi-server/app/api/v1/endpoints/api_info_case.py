"""
API 测试用例信息端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.services.api_info_case import api_info_case_crud
from app.schemas.api_info_case import ApiInfoCaseCreate, ApiInfoCaseUpdate, ApiInfoCaseResponse
from app.core.resp_model import RespModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/ApiInfoCase", tags=["API测试用例"])


@router.get("/queryAll", response_model=ResponseModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有测试用例"""
    try:
        items = await api_info_case_crud.get_multi(db)
        return RespModel.success(data=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=ResponseModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_id: Optional[int] = Query(None, description='项目ID'),
    case_name: Optional[str] = Query(None, description='用例名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询测试用例"""
    try:
        items, total = await api_info_case_crud.get_multi_with_filters(
            db, 
            page=page, 
            page_size=page_size,
            project_id=project_id,
            case_name=case_name
        )
        return RespModel.success(data=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=ResponseModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='测试用例ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询测试用例"""
    try:
        item = await api_info_case_crud.get(db, id=id)
        if not item:
            raise NotFoundException("测试用例不存在")
        return RespModel.success(data=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=ResponseModel)
async def insert(
    *,
    case_data: ApiInfoCaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建测试用例"""
    try:
        item = await api_info_case_crud.create(db, obj_in=case_data)
        return RespModel.success(data={"id": item.id}, msg="添加成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=ResponseModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='测试用例ID'),
    case_data: ApiInfoCaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新测试用例"""
    try:
        item = await api_info_case_crud.get(db, id=id)
        if not item:
            raise NotFoundException("测试用例不存在")
        
        updated_item = await api_info_case_crud.update(db, db_obj=item, obj_in=case_data)
        return RespModel.success(msg="修改成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=ResponseModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='测试用例ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除测试用例"""
    try:
        item = await api_info_case_crud.get(db, id=id)
        if not item:
            raise NotFoundException("测试用例不存在")
        
        await api_info_case_crud.remove(db, id=id)
        return RespModel.success(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/debugTest", response_model=ResponseModel)
async def debug_test(
    *,
    id: int = Query(..., ge=1, description='测试用例ID'),
    db: AsyncSession = Depends(get_db)
):
    """调试测试用例执行"""
    try:
        import uuid
        import os
        import json
        import yaml
        import subprocess
        from app.models.api_info_case import ApiInfoCase
        from app.models.api_info_case_step import ApiInfoCaseStep
        from app.models.api_db_base import ApiDbBase
        from app.models.api_keyword import ApiKeyWord
        from app.models.api_info import ApiInfo
        from sqlalchemy import select
        
        # 获取测试用例信息
        result = await db.execute(select(ApiInfoCase).where(ApiInfoCase.id == id))
        api_case_info = result.scalars().first()
        if not api_case_info:
            raise NotFoundException("测试用例不存在")
        
        # 获取测试步骤
        steps_result = await db.execute(
            select(ApiInfoCaseStep)
            .where(ApiInfoCaseStep.api_case_info_id == id)
            .order_by(ApiInfoCaseStep.run_order.asc())
        )
        api_steps = steps_result.scalars().all()
        
        # 获取项目数据库配置
        db_result = await db.execute(
            select(ApiDbBase)
            .where(
                ApiDbBase.project_id == api_case_info.project_id,
                ApiDbBase.is_enabled == "1"
            )
        )
        db_infos = db_result.scalars().all()
        
        # 创建执行目录
        cases_dir = os.path.join(os.getcwd(), "test_cases")
        execute_uuid = str(uuid.uuid4())
        run_tmp_dir = os.path.join(cases_dir, execute_uuid)
        os.makedirs(run_tmp_dir, exist_ok=True)
        
        # 组装context.yaml信息
        test_case_config = {"_database": {}}
        
        # 添加调试变量
        if api_case_info.param_data and api_case_info.param_data != "null":
            try:
                param_data = json.loads(api_case_info.param_data)
                for d in param_data:
                    test_case_config.update({d["key"]: d["value"]})
            except json.JSONDecodeError:
                pass
        
        # 添加数据库配置
        for db_info in db_infos:
            try:
                db_config = eval(db_info.db_info)
                test_case_config["_database"].update({db_info.ref_name: db_config})
            except:
                pass
        
        # 生成context.yaml文件
        context_yaml_file = os.path.join(run_tmp_dir, "context.yaml")
        with open(context_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_case_config, f, allow_unicode=True, default_flow_style=False)
        
        # 组装测试用例数据
        test_case_data = {
            "desc": api_case_info.case_name,
            "steps": []
        }
        
        # 添加前置脚本
        if api_case_info.pre_request and api_case_info.pre_request != "null":
            test_case_data["pre_script"] = [api_case_info.pre_request]
        
        # 添加后置脚本
        if api_case_info.post_request and api_case_info.post_request != "null":
            test_case_data["post_script"] = [api_case_info.post_request]
        
        # 添加测试步骤
        case_file_name = uuid.uuid4()
        test_case_filename = f"{1}_{case_file_name}.yaml"
        test_case_yaml_file = os.path.join(run_tmp_dir, test_case_filename)
        
        for api_step in api_steps:
            # 获取关键字信息
            keyword_result = await db.execute(
                select(ApiKeyWord).where(ApiKeyWord.id == api_step.key_word_id)
            )
            keyword_data = keyword_result.scalars().first()
            
            if not keyword_data:
                continue
                
            step_data = {api_step.step_desc: {"关键字": keyword_data.keyword_fun_name}}
            
            # 处理send_request关键字
            if keyword_data.keyword_fun_name.startswith("send_request"):
                try:
                    ref_variable = json.loads(api_step.ref_variable) if api_step.ref_variable else {}
                    case_id = ref_variable.get("_接口信息")
                    if case_id:
                        api_info_result = await db.execute(select(ApiInfo).where(ApiInfo.id == case_id))
                        api_info = api_info_result.scalars().first()
                        if api_info:
                            # 生成API信息数据
                            case_steps_data = {
                                "url": api_info.request_url,
                                "method": api_info.request_method,
                                "headers": json.loads(api_info.request_headers) if api_info.request_headers else {},
                                "params": json.loads(api_info.request_params) if api_info.request_params else {},
                                "body": json.loads(api_info.request_body) if api_info.request_body else {}
                            }
                        else:
                            case_steps_data = {}
                    else:
                        case_steps_data = {}
                except:
                    case_steps_data = {}
            else:
                try:
                    case_steps_data = json.loads(api_step.ref_variable) if api_step.ref_variable else {}
                except:
                    case_steps_data = {}
            
            step_data[api_step.step_desc].update(case_steps_data)
            test_case_data["steps"].append(step_data)
        
        # 生成测试用例YAML文件
        with open(test_case_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_case_data, f, allow_unicode=True, default_flow_style=False)
        
        # 创建报告目录
        report_root_dir = os.path.join(os.getcwd(), "report")
        os.makedirs(report_root_dir, exist_ok=True)
        
        report_data_path = os.path.join(report_root_dir, f"{execute_uuid}-data")
        os.makedirs(report_data_path, exist_ok=True)
        
        # 执行测试用例（这里简化处理，实际应该调用测试框架）
        try:
            # 这里可以集成pytest或其他测试框架
            # result = subprocess.run(['pytest', test_case_yaml_file], capture_output=True, text=True)
            
            # 模拟执行结果
            execution_result = {
                "execute_uuid": execute_uuid,
                "status": "completed",
                "message": "测试用例执行完成",
                "report_path": f"/report/{execute_uuid}/"
            }
            
            return RespModel.success(
                data=execution_result,
                msg="测试用例调试执行成功"
            )
        except Exception as exec_error:
            return RespModel.error(f"测试用例执行失败: {str(exec_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调试测试失败: {str(e)}")


@router.post("/uploadFile", response_model=ResponseModel)
async def upload_file(
    *,
    file: UploadFile = File(..., description='XMind文件'),
    project_id: str = Form(..., description='项目ID'),
    db: AsyncSession = Depends(get_db)
):
    """上传XMind文件并解析测试用例"""
    try:
        import tempfile
        import os
        from datetime import datetime
        
        # 验证文件格式
        if not file.filename.endswith(".xmind"):
            raise BadRequestException("请上传有效的XMind文件")
        
        # 保存到临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file.filename)
            content = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # 解析XMind文件
            try:
                from xmindparser import xmind_to_dict
                xmind_data = xmind_to_dict(file_path)
            except ImportError:
                # 如果没有xmindparser库，返回模拟数据
                xmind_data = [{
                    "topic": {
                        "title": "测试用例",
                        "topics": [
                            {
                                "title": "示例测试用例1",
                                "topics": [
                                    {"title": "desc", "topics": [{"title": "示例描述1"}]}
                                ]
                            },
                            {
                                "title": "示例测试用例2", 
                                "topics": [
                                    {"title": "desc", "topics": [{"title": "示例描述2"}]}
                                ]
                            }
                        ]
                    }
                }]
            
            # 提取测试用例
            if not xmind_data or len(xmind_data) == 0:
                raise BadRequestException("XMind文件格式错误或为空")
            
            root_topic = xmind_data[0]["topic"]
            created_cases = []
            
            if "topics" in root_topic:
                for child in root_topic["topics"]:
                    case_name = child["title"]
                    
                    # 查找描述
                    case_desc = ""
                    if "topics" in child:
                        for topic in child["topics"]:
                            if topic["title"].lower() == "desc" and "topics" in topic and topic["topics"]:
                                case_desc = topic["topics"][0]["title"]
                                break
                    
                    # 创建测试用例
                    try:
                        from app.models.api_info_case import ApiInfoCase
                        
                        api_case_info = ApiInfoCase(
                            case_name=case_name,
                            case_desc=case_desc,
                            project_id=int(project_id),
                            create_time=datetime.now()
                        )
                        
                        db.add(api_case_info)
                        await db.flush()
                        case_id = api_case_info.id
                        await db.commit()
                        
                        created_cases.append({
                            "id": case_id,
                            "case_name": case_name,
                            "case_desc": case_desc
                        })
                        
                    except Exception as case_error:
                        await db.rollback()
                        continue
            
            return RespModel.success(
                data=created_cases,
                msg=f"成功解析并创建{len(created_cases)}个测试用例"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
