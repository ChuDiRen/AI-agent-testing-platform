"""
关键字Controller - 已重构为使用Service层
"""
import json
import os
from datetime import datetime

from apitest.service.ApiKeywordService import ApiKeywordService
from config.dev_settings import settings
from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from core.time_utils import TimeFormatter
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.ApiKeyWordModel import ApiKeyWord
from ..model.ApiOperationTypeModel import OperationType
from ..schemas.ApiKeywordSchema import ApiKeyWordQuery, ApiKeyWordCreate, ApiKeyWordUpdate, KeywordFileRequest

logger = get_logger(__name__)

# ==================== 配置常量 ====================
BASE_DIR = settings.BASE_DIR
TEMP_DIR = settings.TEMP_DIR
YAML_DIR = settings.YAML_DIR
REPORT_DIR = settings.REPORT_DIR
LOG_DIR = settings.LOG_DIR

module_name = "ApiKeyWord"
module_model = ApiKeyWord
module_route = APIRouter(prefix=f"/{module_name}", tags=["API关键字管理"])

# ==================== 路由处理函数 ====================

@module_route.get("/queryAll", summary="查询所有关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryAll(session: Session = Depends(get_session)):
    """查询所有关键字"""
    try:
        service = ApiKeywordService(session)
        datas = service.query_all()
        return respModel.ok_resp_list(lst=datas, msg="查询成功")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/queryByPage", summary="分页查询关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))])
async def queryByPage(query: ApiKeyWordQuery, session: Session = Depends(get_session)):
    """分页查询关键字"""
    try:
        service = ApiKeywordService(session)
        datas, total = service.query_by_page(
            page=query.page,
            page_size=query.pageSize,
            keyword_name=query.name,
            operation_type_id=query.operation_type_id
        )
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.get("/queryById", summary="根据ID查询关键字")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询关键字"""
    try:
        service = ApiKeywordService(session)
        data = service.get_by_id(id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.error_resp("关键字不存在")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败: {e}")

@module_route.post("/insert", summary="新增关键字", dependencies=[Depends(check_permission("apitest:keyword:add"))])
async def insert(keyword: ApiKeyWordCreate, session: Session = Depends(get_session)):
    """新增关键字"""
    try:
        service = ApiKeywordService(session)
        data = service.create(**keyword.model_dump())
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@module_route.put("/update", summary="更新关键字", dependencies=[Depends(check_permission("apitest:keyword:edit"))])
async def update(keyword: ApiKeyWordUpdate, session: Session = Depends(get_session)):
    """更新关键字"""
    try:
        service = ApiKeywordService(session)
        # 检查关键字方法名是否与其他记录重复
        if keyword.keyword_fun_name:
            check_statement = select(module_model).where(module_model.keyword_fun_name == keyword.keyword_fun_name)
            existing = session.exec(check_statement).first()
            if existing and existing.id != keyword.id:
                logger.warning(f"关键字方法名重复: {keyword.keyword_fun_name}")
                return respModel.error_resp(msg="数据库已存在重复的关键字方法，请重新输入")

        update_data = keyword.model_dump(exclude_unset=True, exclude={'id'})
        success = service.update(keyword.id, update_data)
        if success:
            logger.info(f"更新关键字成功: ID={keyword.id}")
            return respModel.ok_resp(msg="修改成功")
        else:
            logger.warning(f"更新关键字失败，关键字不存在: ID={keyword.id}")
            return respModel.error_resp(msg="关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新关键字失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@module_route.delete("/delete", summary="删除关键字", dependencies=[Depends(check_permission("apitest:keyword:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除关键字"""
    try:
        service = ApiKeywordService(session)
        success = service.delete(id)
        if success:
            logger.info(f"删除关键字成功: ID={id}")
            return respModel.ok_resp(msg="删除成功")
        else:
            logger.warning(f"删除关键字失败，关键字不存在: ID={id}")
            return respModel.error_resp(msg="关键字不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除关键字失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")

@module_route.delete("/batchDelete", summary="批量删除关键字", dependencies=[Depends(check_permission("apitest:keyword:delete"))])
async def batchDelete(ids: str = Query(..., description="逗号分隔的ID列表"), session: Session = Depends(get_session)):
    """批量删除关键字"""
    try:
        id_list = [int(id.strip()) for id in ids.split(',') if id.strip()]
        if not id_list:
            logger.warning("批量删除失败：未提供有效的ID列表")
            return respModel.error_resp(msg="请提供有效的ID列表")

        service = ApiKeywordService(session)
        deleted_count = service.batch_delete(id_list)
        logger.info(f"批量删除关键字成功，共删除{deleted_count}条记录")
        return respModel.ok_resp(msg=f"批量删除成功，共删除{deleted_count}条记录")
    except Exception as e:
        session.rollback()
        logger.error(f"批量删除关键字失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量删除失败：{e}")

@module_route.post("/keywordFile", summary="生成关键字文件", dependencies=[Depends(check_permission("apitest:keyword:generate"))]) # 生成关键字文件
async def keywordFile(request: KeywordFileRequest):
    try:
        file_name = request.keyword_fun_name
        keyword_value = request.keyword_value
        
        # 验证和格式化代码
        if not keyword_value.strip():
            return respModel.error_resp(msg="关键字代码不能为空")
        
        # 确保代码有正确的编码声明
        if not keyword_value.strip().startswith('# -*- coding:'):
            keyword_value = '# -*- coding: UTF-8 -*-\n' + keyword_value
        
        # 格式化代码（简单格式化）
        formatted_code = format_keyword_code(keyword_value)
        
        keywords_dir = str(settings.KEYWORDS_DIR)
        os.makedirs(keywords_dir, exist_ok=True)
        
        file_path = f'{keywords_dir}/{file_name}.py'
        with open(file_path, 'w', encoding="utf-8") as f:
            f.write(formatted_code)
        
        # 验证文件语法
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            compile(code_content, file_path, 'exec')
        except SyntaxError as e:
            return respModel.error_resp(msg=f"生成的代码有语法错误: {str(e)}")
        
        return respModel.ok_resp(msg="生成文件成功", dic_t={"id": file_name})
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"生成文件失败:{e}")

def format_keyword_code(code: str) -> str:
    """格式化关键字代码"""
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    indent_size = 4
    
    for line in lines:
        stripped_line = line.strip()
        
        # 保留空行
        if stripped_line == '':
            formatted_lines.append('')
            continue
        
        # 处理缩进减少
        if stripped_line.startswith((')', ']', '}')) or \
           stripped_line in ('else:', 'elif:', 'except:', 'finally:'):
            indent_level = max(0, indent_level - 1)
        
        # 添加缩进
        indent = ' ' * (indent_level * indent_size)
        formatted_lines.append(indent + stripped_line)
        
        # 处理缩进增加
        if stripped_line.endswith(':') or \
           stripped_line.endswith(('{', '[', '(')):
            indent_level += 1
    
    return '\n'.join(formatted_lines)

@module_route.get("/queryByOperationType", summary="根据操作类型查询关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))]) # 根据操作类型ID查询关键字列表
async def queryByOperationType(operation_type_id: int = Query(...), session: Session = Depends(get_session)):
    """根据操作类型ID查询关键字列表"""
    try:
        statement = select(module_model).where(module_model.operation_type_id == operation_type_id)
        datas = session.exec(statement).all()
        result = [
            {
                "id": data.id,
                "name": data.name,
                "keyword_fun_name": data.keyword_fun_name,
                "keyword_desc": data.keyword_desc,
                "operation_type_id": data.operation_type_id,
                "is_enabled": data.is_enabled
            } for data in datas
        ]
        return respModel.ok_resp_list(lst=result, msg="查询成功")
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/getKeywordFields", summary="获取关键字字段描述", dependencies=[Depends(check_permission("apitest:keyword:query"))]) # 获取关键字的字段描述
async def getKeywordFields(keyword_id: int = Query(...), session: Session = Depends(get_session)):
    """获取关键字的字段描述（解析keyword_desc或从代码中提取）"""
    try:
        import json
        import re
        
        # 查询关键字
        keyword = session.get(module_model, keyword_id)
        if not keyword:
            return respModel.error_resp("关键字不存在")
        
        # 尝试解析keyword_desc为JSON
        try:
            if keyword.keyword_desc:
                fields = json.loads(keyword.keyword_desc)
                # 这里 keyword_desc 本身就是字段定义列表，直接以数组形式返回
                if isinstance(fields, list):
                    return respModel.ok_resp_simple(lst=fields, msg="查询成功")
                else:
                    return respModel.ok_resp_simple(lst=[fields], msg="查询成功")
        except json.JSONDecodeError:
            # 不是JSON格式，尝试从代码中提取
            pass
        
        # 从keyword_value（函数代码）中提取参数
        fields = []
        if keyword.keyword_value:
            # 匹配 kwargs.get("PARAM_NAME", default) 模式
            pattern = r'kwargs\.get\s*\(\s*["\'](\w+)["\']\s*(?:,\s*([^)]+))?\)'
            matches = re.findall(pattern, keyword.keyword_value)
            
            for param_name, default_value in matches:
                field = {
                    "name": param_name,
                    "type": "string",
                    "required": default_value.strip() == "None" if default_value else True,
                    "description": f"参数: {param_name}",
                    "default": "" if not default_value or default_value.strip() == "None" else default_value.strip().strip("'\"")
                }
                fields.append(field)
        
        # 最终返回字段定义数组
        if fields:
            return respModel.ok_resp_simple(lst=fields, msg="查询成功")
        else:
            return respModel.ok_resp_simple(lst=[], msg="该关键字没有字段描述")
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误: {e}")

@module_route.post("/batchImport", summary="批量导入关键字", dependencies=[Depends(check_permission("apitest:keyword:add"))]) # 批量导入关键字
async def batchImport(file: str = Query(..., description="文件内容"), session: Session = Depends(get_session)):
    try:
        import json
        import csv
        import io
        
        # 尝试解析JSON格式
        try:
            keywords_data = json.loads(file)
            if not isinstance(keywords_data, list):
                return respModel.error_resp(msg="文件格式错误，应为关键字数组")
        except json.JSONDecodeError:
            # 尝试解析CSV格式
            try:
                csv_reader = csv.DictReader(io.StringIO(file))
                keywords_data = []
                for row in csv_reader:
                    keywords_data.append({
                        "name": row.get("name", ""),
                        "keyword_fun_name": row.get("keyword_fun_name", ""),
                        "keyword_value": row.get("keyword_value", ""),
                        "keyword_desc": row.get("keyword_desc", "[]"),
                        "operation_type_id": int(row.get("operation_type_id", 0)),
                        "is_enabled": row.get("is_enabled", "1"),
                        "category": row.get("category", "")
                    })
            except Exception as e:
                return respModel.error_resp(msg=f"文件格式错误，仅支持JSON或CSV格式: {e}")

        if not keywords_data:
            logger.warning("批量导入失败：文件中没有有效数据")
            return respModel.error_resp(msg="文件中没有有效数据")

        service = ApiKeywordService(session)
        imported_keywords = []
        errors = []

        for i, keyword_data in enumerate(keywords_data):
            try:
                # 验证必填字段
                if not keyword_data.get("name") or not keyword_data.get("keyword_fun_name"):
                    errors.append(f"第{i+1}行：关键字名称和函数名不能为空")
                    continue

                # 检查函数名是否重复
                check_statement = select(module_model).where(module_model.keyword_fun_name == keyword_data["keyword_fun_name"])
                existing = session.exec(check_statement).first()
                if existing:
                    errors.append(f"第{i+1}行：函数名'{keyword_data['keyword_fun_name']}'已存在")
                    continue

                # 准备关键字数据
                keyword_dict = {
                    "name": keyword_data["name"],
                    "keyword_fun_name": keyword_data["keyword_fun_name"],
                    "keyword_value": keyword_data.get("keyword_value", ""),
                    "keyword_desc": keyword_data.get("keyword_desc", "[]"),
                    "operation_type_id": keyword_data.get("operation_type_id", 0),
                    "is_enabled": keyword_data.get("is_enabled", "1"),
                    "category": keyword_data.get("category", "")
                }
                imported_keywords.append(keyword_dict)

            except Exception as e:
                errors.append(f"第{i+1}行：{str(e)}")
                continue

        # 批量创建
        imported_count = 0
        if imported_keywords:
            created_keywords = service.batch_create(imported_keywords)
            imported_count = len(created_keywords)

        result_msg = f"批量导入完成，成功导入{imported_count}条记录"
        if errors:
            result_msg += f"，失败{len(errors)}条。错误详情：{'; '.join(errors[:5])}"
            if len(errors) > 5:
                result_msg += f"等{len(errors)}个错误"

        logger.info(f"批量导入关键字完成: 成功{imported_count}条, 失败{len(errors)}条")
        return respModel.ok_resp(msg=result_msg, dic_t={"imported_count": imported_count, "errors": errors})
        
    except Exception as e:
        session.rollback()
        logger.error(f"批量导入失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量导入失败：{e}")

@module_route.get("/batchExport", summary="批量导出关键字", dependencies=[Depends(check_permission("apitest:keyword:query"))]) # 批量导出关键字
async def batchExport(ids: str = Query(None, description="逗号分隔的ID列表，为空则导出所有"), 
                     session: Session = Depends(get_session)):
    try:
        if ids:
            id_list = [int(id.strip()) for id in ids.split(',') if id.strip()]
            statement = select(module_model).where(module_model.id.in_(id_list))
        else:
            statement = select(module_model)
        
        keywords = session.exec(statement).all()
        
        if not keywords:
            return respModel.error_resp(msg="没有找到要导出的关键字")
        
        # 转换为字典格式
        export_data = []
        for keyword in keywords:
            export_data.append({
                "id": keyword.id,
                "name": keyword.name,
                "keyword_fun_name": keyword.keyword_fun_name,
                "keyword_value": keyword.keyword_value,
                "keyword_desc": keyword.keyword_desc,
                "operation_type_id": keyword.operation_type_id,
                "is_enabled": keyword.is_enabled,
                "category": keyword.category,
                "create_time": keyword.create_time.isoformat() if keyword.create_time else ""
            })
        
        # 生成JSON格式
        content = json.dumps(export_data, ensure_ascii=False, indent=2)
        filename = f"keywords_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return respModel.ok_resp(msg="导出成功", dic_t={
            "content": content,
            "filename": filename,
            "count": len(export_data)
        })
        
    except Exception as e:
        logger.error(f"批量导出失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"批量导出失败：{e}")
