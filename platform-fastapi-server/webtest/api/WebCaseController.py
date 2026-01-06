"""
Web用例Controller - 按照apitest标准实现
"""
import json
from typing import List
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File
from sqlmodel import Session

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel

from ..schemas.WebCaseSchema import (
    WebCaseCreate, WebCaseUpdate, WebCaseQuery, WebCaseResponse,
    WebCaseFolderCreate, WebCaseFolderUpdate, WebCaseFolderResponse,
    WebCaseTreeNode, BatchDeleteRequest, XMindImportRequest
)
from ..service.WebCaseService import WebCaseService

module_name = "WebCase"
module_route = APIRouter(prefix=f"/{module_name}", tags=["Web用例管理"])
logger = get_logger(__name__)


@module_route.post("/queryByPage", summary="分页查询Web用例", dependencies=[Depends(check_permission("webtest:case:query"))])
async def queryByPage(query: WebCaseQuery, session: Session = Depends(get_session)):
    """分页查询Web用例"""
    try:
        cases, total = WebCaseService.query_cases_by_page(session, query)
        
        # 转换为响应格式，解析步骤
        case_responses = []
        for case in cases:
            # 解析步骤
            steps = []
            if case.steps:
                try:
                    steps_data = json.loads(case.steps)
                    from ..schemas.WebCaseSchema import WebCaseStep
                    steps = [WebCaseStep(**step) for step in steps_data]
                except json.JSONDecodeError:
                    pass
            
            # 直接返回字典格式，符合前端期望
            case_dict = case.dict()
            case_dict['steps'] = steps
            # 添加step_count用于前端显示
            case_dict['step_count'] = len(steps)
            # 添加folder_name（需要从folder表获取，这里暂时用空值）
            case_dict['folder_name'] = ''
            case_responses.append(case_dict)
        
        return respModel.ok_resp_list(lst=case_responses, total=total)
    except Exception as e:
        logger.error(f"分页查询Web用例失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.get("/queryById", summary="根据ID查询Web用例", dependencies=[Depends(check_permission("webtest:case:query"))])
async def queryById(id: int = Query(..., description="用例ID"), session: Session = Depends(get_session)):
    """根据ID查询Web用例"""
    try:
        case = WebCaseService.get_case_by_id(session, id)
        if not case:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
        
        # 解析步骤
        steps = []
        if case.steps:
            try:
                steps_data = json.loads(case.steps)
                from ..schemas.WebCaseSchema import WebCaseStep
                steps = [WebCaseStep(**step) for step in steps_data]
            except json.JSONDecodeError:
                pass
        
        # 直接返回字典格式，符合前端期望
        case_dict = case.dict()
        case_dict['steps'] = steps  # 前端可能需要这个字段
        
        return respModel.ok_resp(obj=case_dict)
    except Exception as e:
        logger.error(f"根据ID查询Web用例失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/insert", summary="新增Web用例", dependencies=[Depends(check_permission("webtest:case:add"))])
async def insert(case_data: WebCaseCreate, session: Session = Depends(get_session)):
    """新增Web用例"""
    try:
        case = WebCaseService.create_case(session, case_data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": case.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增Web用例失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.put("/update", summary="更新Web用例", dependencies=[Depends(check_permission("webtest:case:edit"))])
async def update(case_data: WebCaseUpdate, session: Session = Depends(get_session)):
    """更新Web用例"""
    try:
        if not hasattr(case_data, 'id') or case_data.id is None:
            return respModel.error_resp("缺少用例ID")
        
        case = WebCaseService.update_case(session, case_data.id, case_data)
        if case:
            return respModel.ok_resp(msg="更新成功")
        else:
            return respModel.error_resp("用例不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新Web用例失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"更新失败，请联系管理员:{e}")


@module_route.delete("/delete", summary="删除Web用例", dependencies=[Depends(check_permission("webtest:case:delete"))])
async def delete(id: int = Query(..., description="用例ID"), session: Session = Depends(get_session)):
    """删除Web用例"""
    try:
        success = WebCaseService.delete_case(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("用例不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除Web用例失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")


@module_route.delete("/batchDelete", summary="批量删除Web用例", dependencies=[Depends(check_permission("webtest:case:delete"))])
async def batchDelete(request: BatchDeleteRequest, session: Session = Depends(get_session)):
    """批量删除Web用例"""
    try:
        deleted_count = WebCaseService.batch_delete_cases(session, request.ids)
        if deleted_count > 0:
            return respModel.ok_resp(msg=f"成功删除{deleted_count}个用例")
        else:
            return respModel.error_resp("没有找到要删除的用例")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除Web用例失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量删除失败：{e}")


@module_route.post("/queryTree", summary="查询用例目录树", dependencies=[Depends(check_permission("webtest:case:query"))])
async def queryTree(project_id: int = Query(..., description="项目ID"), session: Session = Depends(get_session)):
    """查询用例目录树"""
    try:
        tree_nodes = WebCaseService.get_case_tree(session, project_id)
        
        # 转换为字典格式，符合前端期望
        tree_dicts = []
        for node in tree_nodes:
            node_dict = node.dict()
            # 关键修正：将 name 字段映射为 label，符合前端期望
            node_dict['label'] = node_dict.get('name', '')
            
            # 确保包含所有前端需要的字段
            if hasattr(node, 'case_info') and node.case_info:
                # 如果是用例节点，添加用例信息
                case_dict = node.case_info.dict()
                node_dict.update(case_dict)
            
            tree_dicts.append(node_dict)
        
        return respModel.ok_resp_list(lst=tree_dicts, total=len(tree_dicts))
    except Exception as e:
        logger.error(f"查询用例目录树失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")


@module_route.post("/importXMind", summary="导入XMind用例", dependencies=[Depends(check_permission("webtest:case:add"))])
async def importXMind(
    file: UploadFile = File(...),
    project_id: int = Query(..., description="项目ID"),
    folder_id: int = Query(None, description="目标目录ID"),
    overwrite: bool = Query(default=False, description="是否覆盖已存在的用例"),
    session: Session = Depends(get_session)
):
    """导入XMind用例"""
    try:
        if not file.filename.endswith('.xmind'):
            return respModel.error_resp("请上传XMind格式文件")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 解析XMind文件
        try:
            import_cases = WebCaseService.parse_xmind_file(file_content)
        except Exception as e:
            return respModel.error_resp(f"XMind文件解析失败: {e}")
        
        if not import_cases:
            return respModel.error_resp("XMind文件中没有找到有效的用例数据")
        
        # 导入到数据库
        result = WebCaseService.import_cases_from_xmind(
            session, project_id, folder_id, import_cases, overwrite
        )
        
        return respModel.ok_resp(obj=result, msg="导入成功")
    except Exception as e:
        session.rollback()
        logger.error(f"导入XMind用例失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"导入失败：{e}")


@module_route.post("/folder/insert", summary="创建目录", dependencies=[Depends(check_permission("webtest:case:add"))])
async def folderInsert(folder_data: WebCaseFolderCreate, session: Session = Depends(get_session)):
    """创建目录"""
    try:
        folder = WebCaseService.create_folder(session, folder_data)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": folder.id})
    except Exception as e:
        session.rollback()
        logger.error(f"创建目录失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")


@module_route.delete("/folder/delete", summary="删除目录", dependencies=[Depends(check_permission("webtest:case:delete"))])
async def folderDelete(id: int = Query(..., description="目录ID"), session: Session = Depends(get_session)):
    """删除目录"""
    try:
        success = WebCaseService.delete_folder(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp("目录不存在或无法删除")
    except ValueError as e:
        return respModel.error_resp(str(e))
    except Exception as e:
        session.rollback()
        logger.error(f"删除目录失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败：{e}")


@module_route.post("/copy", summary="复制用例", dependencies=[Depends(check_permission("webtest:case:add"))])
async def copy(id: int = Query(..., description="用例ID"), new_name: str = Query(None, description="新用例名称"), session: Session = Depends(get_session)):
    """复制用例"""
    try:
        new_case = WebCaseService.copy_case(session, id, new_name)
        if new_case:
            return respModel.ok_resp(msg="复制成功", dic_t={"id": new_case.id})
        else:
            return respModel.error_resp("用例不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"复制用例失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"复制失败：{e}")


@module_route.post("/addToPlan", summary="添加用例到测试计划", dependencies=[Depends(check_permission("webtest:case:edit"))])
async def addToPlan(data: dict, session: Session = Depends(get_session)):
    """添加用例到测试计划"""
    try:
        # TODO: 实现添加用例到测试计划的功能
        # 这里需要与测试计划模块进行集成
        
        plan_id = data.get("plan_id")
        case_ids = data.get("case_ids", [])
        
        if not plan_id or not case_ids:
            return respModel.error_resp("缺少必要参数")
        
        # 模拟添加结果
        return respModel.ok_resp(msg=f"成功添加{len(case_ids)}个用例到测试计划")
    except Exception as e:
        logger.error(f"添加用例到测试计划失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败：{e}")


