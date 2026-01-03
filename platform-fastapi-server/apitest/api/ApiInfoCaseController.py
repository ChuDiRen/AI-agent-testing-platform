"""
接口用例Controller - 已重构为使用Service层
"""
import json
from datetime import datetime

import yaml
from apitest.service.ApiInfoCaseService import InfoCaseService
from config.dev_settings import settings
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..model.ApiKeyWordModel import ApiKeyWord
from ..model.ApiHistoryModel import ApiHistory
from ..schemas.ApiInfoCaseSchema import (
    ApiInfoCaseQuery, ApiInfoCaseCreate, ApiInfoCaseUpdate,
    YamlGenerateRequest,
    ApiInfoCaseExecuteRequest
)

logger = get_logger(__name__)

# ==================== 配置常量 ====================
BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
YAML_DIR = settings.YAML_DIR
REPORT_DIR = settings.REPORT_DIR
LOG_DIR = settings.LOG_DIR

module_name = "ApiInfoCase"
module_model = ApiInfoCase
module_route = APIRouter(prefix=f"/{module_name}", tags=["API用例管理"])

# ==================== 路由处理函数 ====================

@module_route.post("/queryByPage", summary="分页查询API用例", dependencies=[Depends(check_permission("apitest:case:query"))])
async def queryByPage(query: ApiInfoCaseQuery, session: Session = Depends(get_session)):
    """分页查询用例"""
    try:
        datas, total = InfoCaseService.query_by_page(session, query)
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.get("/queryById", summary="根据ID查询用例")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询用例（含步骤）"""
    try:
        case = InfoCaseService.query_by_id(session, id)
        if not case:
            return respModel.error_resp("用例不存在")
        
        # 查询步骤
        steps = session.exec(
            select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == id).order_by(ApiInfoCaseStep.run_order)
        ).all()
        
        # 构建返回数据
        result = {
            "id": case.id,
            "project_id": case.project_id,
            "case_name": case.case_name,
            "case_desc": case.case_desc,
            "context_config": json.loads(case.context_config) if case.context_config else None,
            "ddts": json.loads(case.ddts) if case.ddts else None,
            "pre_request": case.pre_request,
            "post_request": case.post_request,
            "create_time": TimeFormatter.format_datetime(case.create_time),
            "update_time": TimeFormatter.format_datetime(case.update_time),
            "steps": [
                {
                    "id": step.id,
                    "run_order": step.run_order,
                    "step_desc": step.step_desc,
                    "operation_type_id": step.operation_type_id,
                    "keyword_id": step.keyword_id,
                    "api_info_id": step.api_info_id,
                    "step_data": json.loads(step.step_data) if step.step_data else {}
                }
                for step in steps
            ]
        }
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/insert", summary="新增API用例", dependencies=[Depends(check_permission("apitest:case:add"))])
async def insert(case_data: ApiInfoCaseCreate, session: Session = Depends(get_session)):
    """新增用例（含步骤）"""
    try:
        # 创建用例
        new_case = ApiInfoCase(
            project_id=case_data.project_id,
            case_name=case_data.case_name,
            case_desc=case_data.case_desc,
            context_config=json.dumps(case_data.context_config, ensure_ascii=False) if case_data.context_config else None,
            ddts=json.dumps(case_data.ddts, ensure_ascii=False) if case_data.ddts else None,
            pre_request=case_data.pre_request,
            post_request=case_data.post_request,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        session.add(new_case)
        session.flush()
        
        # 创建步骤
        if case_data.steps:
            for step in case_data.steps:
                new_step = ApiInfoCaseStep(
                    case_info_id=new_case.id,
                    run_order=step.run_order,
                    step_desc=step.step_desc,
                    operation_type_id=step.operation_type_id,
                    keyword_id=step.keyword_id,
                    api_info_id=step.api_info_id if hasattr(step, 'api_info_id') else None,
                    step_data=json.dumps(step.step_data, ensure_ascii=False) if step.step_data else None,
                    create_time=datetime.now()
                )
                session.add(new_step)
        
        session.commit()
        return respModel.ok_resp(obj={"id": new_case.id}, msg="新增成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update", summary="更新API用例", dependencies=[Depends(check_permission("apitest:case:edit"))])
async def update(case_data: ApiInfoCaseUpdate, session: Session = Depends(get_session)):
    """更新用例（含步骤）"""
    try:
        case = session.get(ApiInfoCase, case_data.id)
        if not case:
            return respModel.error_resp("用例不存在")
        
        # 更新用例基本信息
        if case_data.project_id is not None:
            case.project_id = case_data.project_id
        if case_data.case_name is not None:
            case.case_name = case_data.case_name
        if case_data.case_desc is not None:
            case.case_desc = case_data.case_desc
        if case_data.context_config is not None:
            case.context_config = json.dumps(case_data.context_config, ensure_ascii=False)
        if case_data.ddts is not None:
            case.ddts = json.dumps(case_data.ddts, ensure_ascii=False)
        if case_data.pre_request is not None:
            case.pre_request = case_data.pre_request
        if case_data.post_request is not None:
            case.post_request = case_data.post_request
        case.update_time = datetime.now()
        
        # 更新步骤（如果提供）
        if case_data.steps is not None:
            # 删除旧步骤
            old_steps = session.exec(select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == case_data.id)).all()
            for old_step in old_steps:
                session.delete(old_step)
            
            # 创建新步骤
            for step in case_data.steps:
                new_step = ApiInfoCaseStep(
                    case_info_id=case_data.id,
                    run_order=step.run_order,
                    step_desc=step.step_desc,
                    operation_type_id=step.operation_type_id,
                    keyword_id=step.keyword_id,
                    api_info_id=step.api_info_id if hasattr(step, 'api_info_id') else None,
                    step_data=json.dumps(step.step_data, ensure_ascii=False) if step.step_data else None,
                    create_time=datetime.now()
                )
                session.add(new_step)
        
        session.commit()
        return respModel.ok_resp_text(msg="更新成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.delete("/delete", summary="删除API用例", dependencies=[Depends(check_permission("apitest:case:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除用例（含关联步骤）"""
    try:
        obj = session.get(module_model, id)
        if obj:
            # 先删除关联的步骤
            steps = session.exec(select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == id)).all()
            for step in steps:
                session.delete(step)
            # 再删除用例
            session.delete(obj)
            session.commit()
            return respModel.ok_resp_text(msg="删除成功")
        return respModel.error_resp("数据不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getSteps", summary="获取用例步骤", dependencies=[Depends(check_permission("apitest:case:query"))])
async def getSteps(case_id: int = Query(...), session: Session = Depends(get_session)):
    """获取用例的所有步骤"""
    try:
        statement = select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == case_id).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()
        
        def parse_step_data(step_data_str):
            if not step_data_str:
                return {}
            try:
                return json.loads(step_data_str)
            except:
                return {}
        
        result = [
            {
                "id": step.id,
                "case_info_id": step.case_info_id,
                "run_order": step.run_order,
                "step_desc": step.step_desc,
                "operation_type_id": step.operation_type_id,
                "keyword_id": step.keyword_id,
                "step_data": parse_step_data(step.step_data),
                "create_time": TimeFormatter.format_datetime(step.create_time)
            } for step in steps
        ]
        
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/generateYaml", summary="生成用例YAML文件", dependencies=[Depends(check_permission("apitest:case:generate"))])
async def generateYaml(request: YamlGenerateRequest, session: Session = Depends(get_session)):
    """生成用例YAML文件"""
    try:
        # 查询用例信息
        case_info = session.get(ApiInfoCase, request.case_id)
        if not case_info:
            return respModel.error_resp("用例不存在")
        
        # 查询用例步骤
        statement = select(ApiInfoCaseStep).where(ApiInfoCaseStep.case_info_id == request.case_id).order_by(ApiInfoCaseStep.run_order)
        steps = session.exec(statement).all()
        
        if not steps:
            return respModel.error_resp("用例没有步骤")
        
        # 构建YAML内容
        yaml_data = {
            'desc': case_info.case_name,
            'steps': []
        }
        
        # 转换步骤为YAML格式
        for step in steps:
            # 解析步骤数据
            step_data_dict = json.loads(step.step_data) if step.step_data else {}
            
            # 获取关键字信息
            keyword = session.get(ApiKeyWord, step.keyword_id) if step.keyword_id else None
            keyword_name = keyword.keyword_fun_name if keyword else "unknown"
            
            # 构建步骤
            step_item = {
                step.step_desc or f"步骤{step.run_order}": {
                    '关键字': keyword_name,
                    **step_data_dict
                }
            }
            yaml_data['steps'].append(step_item)
        
        # 添加上下文变量
        if request.context_vars:
            yaml_data['ddts'] = [{
                'desc': f'{case_info.case_name}_数据',
                **request.context_vars
            }]
        
        # 生成YAML内容
        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # 保存到文件
        YAML_DIR.mkdir(parents=True, exist_ok=True)
        yaml_filename = f"{case_info.case_name}_{request.case_id}.yaml"
        yaml_file_path = YAML_DIR / yaml_filename
        yaml_file_path.write_text(yaml_content, encoding='utf-8')
        
        return respModel.ok_resp(dic_t={
            "yaml_content": yaml_content,
            "file_path": str(yaml_file_path)
        }, msg="YAML生成成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.post("/executeCase", summary="执行用例测试（异步）", dependencies=[Depends(check_permission("apitest:case:execute"))])
async def executeCase(
    request: ApiInfoCaseExecuteRequest,
    session: Session = Depends(get_session)
):
    """
    异步执行用例测试
    支持两种模式：
    - 单用例执行：提供 case_id
    - 批量执行计划：提供 plan_id

    接口立即返回 test_id，前端通过 /executionStatus 接口轮询结果
    """
    from ..service.execution_service import ExecutionService

    try:
        # 参数校验
        if not request.case_id and not request.plan_id:
            return respModel.error_resp("请提供 case_id 或 plan_id")

        exec_service = ExecutionService(session)

        # 执行（内部自动提交后台任务）
        if request.plan_id:
            result = exec_service.execute_plan(
                plan_id=request.plan_id,
                test_name=request.test_name
            )
            return respModel.ok_resp(dic_t=result, msg="测试计划已提交，请通过 executionStatus 接口查询结果")

        # 单用例执行
        result = exec_service.execute_case(
            case_id=request.case_id,
            test_name=request.test_name,
            context_vars=request.context_vars
        )
        return respModel.ok_resp(dic_t=result, msg="用例测试已提交，请通过 executionStatus 接口查询结果")
        
    except ValueError as e:
        return respModel.error_resp(str(e))
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {str(e)}")


@module_route.get("/executionStatus", summary="查询用例执行状态", dependencies=[Depends(check_permission("apitest:case:query"))])
async def executionStatus(test_id: int = Query(..., description="测试ID"), session: Session = Depends(get_session)):
    """
    查询用例执行状态
    前端轮询此接口获取执行结果
    """
    try:
        history = session.get(ApiHistory, test_id)
        if not history:
            return respModel.error_resp("测试记录不存在")

        result = {
            "test_id": history.id,
            "status": history.test_status,
            "test_name": history.test_name,
            "error_message": history.error_message,
            "yaml_content": history.yaml_content,
            "response_data": history.response_data,
            "create_time": TimeFormatter.datetime_to_str(history.create_time) if history.create_time else None,
            "finish_time": TimeFormatter.datetime_to_str(history.finish_time) if history.finish_time else None,
        }

        # 判断是否完成
        is_finished = history.test_status in ["completed", "passed", "failed", "error"]
        
        return respModel.ok_resp(
            dic_t={"data": result, "finished": is_finished},
            msg="查询成功"
        )
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {str(e)}")


@module_route.get("/getCaseEngines", summary="获取用例使用的引擎列表", dependencies=[Depends(check_permission("apitest:case:query"))])
async def getCaseEngines(case_id: int = Query(..., description="用例ID"), session: Session = Depends(get_session)):
    """
    获取用例使用的所有引擎列表
    用于前端显示用例使用了哪些引擎
    """
    try:
        return respModel.ok_resp(obj={
            "engines": [{
                "plugin_code": "api_engine",
                "plugin_name": "API引擎",
                "plugin_id": None
            }],
            "count": 1
        })
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {str(e)}")


# ==================== XMind导入功能 ====================

from fastapi import UploadFile, File

@module_route.post("/importXMind", summary="从XMind文件导入测试用例", dependencies=[Depends(check_permission("apitest:case:add"))])
async def importXMind(
    file: UploadFile = File(..., description="XMind文件"),
    project_id: int = Query(..., description="项目ID"),
    session: Session = Depends(get_session)
):
    """
    从XMind文件批量导入测试用例和步骤
    
    XMind结构约定：
    - 中心主题：项目/模块名称（忽略）
    - 一级子主题：测试用例名称
    - 二级子主题：测试步骤描述
    - 三级子主题：步骤参数（key:value格式）
    
    支持的XMind格式：.xmind（XMind 8及以上版本）
    """
    import zipfile
    import json
    import tempfile
    import os
    
    try:
        # 1. 验证文件类型
        if not file.filename.endswith('.xmind'):
            return respModel.error_resp("请上传.xmind格式的文件")
        
        # 2. 保存上传的文件到临时目录
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xmind') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # 3. 解析XMind文件（XMind文件本质是ZIP压缩包）
            xmind_data = None
            with zipfile.ZipFile(tmp_path, 'r') as zf:
                # XMind 8+ 使用 content.json
                if 'content.json' in zf.namelist():
                    with zf.open('content.json') as f:
                        xmind_data = json.load(f)
                # 旧版本使用 content.xml
                elif 'content.xml' in zf.namelist():
                    return respModel.error_resp("暂不支持旧版XMind格式，请使用XMind 8及以上版本")
                else:
                    return respModel.error_resp("无法解析XMind文件，请检查文件格式")
            
            if not xmind_data:
                return respModel.error_resp("XMind文件内容为空")
            
            # 4. 解析XMind结构
            imported_cases = []
            failed_cases = []
            
            # 获取根主题
            root_topic = xmind_data[0].get('rootTopic', {}) if isinstance(xmind_data, list) else xmind_data.get('rootTopic', {})
            
            # 遍历一级子主题（测试用例）
            case_topics = root_topic.get('children', {}).get('attached', [])
            
            for case_topic in case_topics:
                try:
                    case_name = case_topic.get('title', '').strip()
                    if not case_name:
                        continue
                    
                    # 创建测试用例
                    new_case = module_model(
                        project_id=project_id,
                        case_name=case_name,
                        case_desc=case_topic.get('notes', {}).get('plain', {}).get('content', ''),
                        create_time=datetime.now()
                    )
                    session.add(new_case)
                    session.flush()
                    
                    # 遍历二级子主题（测试步骤）
                    step_topics = case_topic.get('children', {}).get('attached', [])
                    step_order = 1
                    
                    for step_topic in step_topics:
                        step_desc = step_topic.get('title', '').strip()
                        if not step_desc:
                            continue
                        
                        # 解析三级子主题（步骤参数）
                        step_data = {}
                        param_topics = step_topic.get('children', {}).get('attached', [])
                        for param_topic in param_topics:
                            param_text = param_topic.get('title', '').strip()
                            if ':' in param_text:
                                key, value = param_text.split(':', 1)
                                step_data[key.strip()] = value.strip()
                            elif '：' in param_text:  # 支持中文冒号
                                key, value = param_text.split('：', 1)
                                step_data[key.strip()] = value.strip()
                        
                        # 创建测试步骤
                        new_step = ApiInfoCaseStep(
                            case_info_id=new_case.id,
                            step_desc=step_desc,
                            step_data=json.dumps(step_data, ensure_ascii=False) if step_data else None,
                            run_order=step_order,
                            create_time=datetime.now()
                        )
                        session.add(new_step)
                        step_order += 1
                    
                    imported_cases.append({
                        "case_id": new_case.id,
                        "case_name": case_name,
                        "step_count": step_order - 1
                    })
                    
                except Exception as e:
                    failed_cases.append({
                        "case_name": case_topic.get('title', 'Unknown'),
                        "error": str(e)
                    })
            
            session.commit()
            
            result = {
                "imported_count": len(imported_cases),
                "failed_count": len(failed_cases),
                "imported_cases": imported_cases,
                "failed_cases": failed_cases
            }
            
            return respModel.ok_resp(
                obj=result,
                msg=f"导入完成：成功{len(imported_cases)}个，失败{len(failed_cases)}个"
            )
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except zipfile.BadZipFile:
        return respModel.error_resp("无效的XMind文件，请检查文件是否损坏")
    except Exception as e:
        session.rollback()
        logger.error(f"导入XMind失败: {e}", exc_info=True)
        return respModel.error_resp(f"导入失败: {str(e)}")
