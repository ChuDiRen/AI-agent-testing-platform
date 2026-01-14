# -*- coding: utf-8 -*-
"""代码生成器-核心控制器"""
import io
import zipfile
from datetime import datetime

from app.database.database import get_session
from app.dependencies.dependencies import check_permission
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.models.GenHistory import GenHistory
from app.models.GenTable import GenTable
from app.models.GenTableColumn import GenTableColumn
from app.schemas.GeneratorSchema import GenerateRequest, GeneratePreviewRequest, GenerateBatchRequest
from app.services.ASTCodeGenerator import ASTCodeGenerator
from app.services.GeneratorService import GeneratorService

module_route = APIRouter(prefix="/Generator", tags=["代码生成器"])
logger = get_logger(__name__)

@module_route.post("/preview", summary="预览生成代码")
async def preview(request: GeneratePreviewRequest, session: Session = Depends(get_session)):
    """预览生成的代码"""
    try:
        table = session.get(GenTable, request.table_id)
        if not table:
            return respModel.error_resp("表配置不存在")
        
        statement = select(GenTableColumn).where(GenTableColumn.table_id == request.table_id).order_by(GenTableColumn.sort)
        columns = session.exec(statement).all()
        
        if not columns:
            return respModel.error_resp("表字段配置不存在")
        
        generator = ASTCodeGenerator()
        code_files = generator.generate_code(table, columns)
        
        if not code_files:
            return respModel.error_resp("代码生成失败")
        
        try:
            gen_service = GeneratorService(session)
            gen_service.create_history(
                table_id=request.table_id,
                table_name=table.table_name,
                gen_type='0',
                gen_content=str(code_files),
                file_count=len(code_files),
                status='1'
            )
            logger.info(f"保存代码生成历史成功: table_id={request.table_id}")
        except Exception as e:
            logger.warning(f"保存生成历史失败: {e}")
        
        return respModel.ok_resp(obj=code_files, msg="代码预览成功")
    
    except Exception as e:
        logger.error(f"代码预览失败: {e}", exc_info=True)
        return respModel.error_resp(f"代码预览失败:{e}")

@module_route.post("/download", summary="下载生成代码")
async def download(request: GenerateRequest, session: Session = Depends(get_session)):
    """下载生成的代码(ZIP压缩包)"""
    try:
        table = session.get(GenTable, request.table_id)
        if not table:
            return respModel.error_resp("表配置不存在")
        
        statement = select(GenTableColumn).where(GenTableColumn.table_id == request.table_id).order_by(GenTableColumn.sort)
        columns = session.exec(statement).all()
        
        table_info = {
            'table_name': table.table_name,
            'table_comment': table.table_comment,
            'class_name': table.class_name,
            'module_name': table.module_name,
            'business_name': table.business_name,
            'function_name': table.function_name
        }
        
        column_list = [
            {
                'column_name': col.column_name,
                'column_comment': col.column_comment,
                'column_type': col.column_type,
                'python_type': col.python_type,
                'python_field': col.python_field,
                'is_pk': col.is_pk,
                'is_increment': col.is_increment,
                'is_required': col.is_required,
                'is_insert': col.is_insert,
                'is_edit': col.is_edit,
                'is_list': col.is_list,
                'is_query': col.is_query,
                'query_type': col.query_type,
                'sort': col.sort
            }
            for col in columns
        ]
        
        generator = ASTCodeGenerator()
        code_files = generator.generate_code(table, columns)
        
        if not code_files:
            return respModel.error_resp("代码生成失败")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 后端代码
            if 'model' in code_files:
                zip_file.writestr(f"backend/{table.module_name}/models/{table.class_name}Model.py", code_files['model'])
            
            if 'schema' in code_files:
                zip_file.writestr(f"backend/{table.module_name}/schemas/{table.class_name}Schema.py", code_files['schema'])
            
            if 'service' in code_files:
                zip_file.writestr(f"backend/{table.module_name}/services/{table.class_name}Service.py", code_files['service'])
            
            if 'controller' in code_files:
                zip_file.writestr(f"backend/{table.module_name}/api/{table.class_name}Controller.py", code_files['controller'])
            
            # 前端代码
            if 'list.vue' in code_files:
                zip_file.writestr(f"frontend/{table.business_name}/{table.business_name}List.vue", code_files['list.vue'])
            
            if 'form.vue' in code_files:
                zip_file.writestr(f"frontend/{table.business_name}/{table.business_name}Form.vue", code_files['form.vue'])
            
            if 'api.js' in code_files:
                zip_file.writestr(f"frontend/{table.business_name}/{table.business_name}.js", code_files['api.js'])
            
            # 前端公共组件
            if 'BaseSearch.vue' in code_files:
                zip_file.writestr(f"frontend/components/BaseSearch/index.vue", code_files['BaseSearch.vue'])
            
            if 'BaseTable.vue' in code_files:
                zip_file.writestr(f"frontend/components/BaseTable/index.vue", code_files['BaseTable.vue'])
            
            if 'BasePagination.vue' in code_files:
                zip_file.writestr(f"frontend/components/BasePagination/index.vue", code_files['BasePagination.vue'])
            
            if 'BaseForm.vue' in code_files:
                zip_file.writestr(f"frontend/components/BaseForm/index.vue", code_files['BaseForm.vue'])
            
            # 工具函数
            if 'timeFormatter.js' in code_files:
                zip_file.writestr(f"frontend/utils/timeFormatter.js", code_files['timeFormatter.js'])
            
            # README
            readme_content = f"""# {table.function_name} 代码生成说明

## 表信息
- 表名: {table.table_name}
- 类名: {table.class_name}
- 模块名: {table.module_name}
- 业务名: {table.business_name}

## 后端文件
- Model: backend/{table.module_name}/models/{table.class_name}Model.py
- Schema: backend/{table.module_name}/schemas/{table.class_name}Schema.py
- Service: backend/{table.module_name}/services/{table.class_name}Service.py
- Controller: backend/{table.module_name}/api/{table.class_name}Controller.py

## 前端文件
- 列表页: frontend/{table.business_name}/{table.business_name}List.vue
- 表单页: frontend/{table.business_name}/{table.business_name}Form.vue
- API: frontend/{table.business_name}/{table.business_name}.js

## 前端公共组件
- BaseSearch: frontend/components/BaseSearch/index.vue
- BaseTable: frontend/components/BaseTable/index.vue
- BasePagination: frontend/components/BasePagination/index.vue
- BaseForm: frontend/components/BaseForm/index.vue

## 前端文件
- 列表页: frontend/{table.business_name}/{table.business_name}List.vue
- 表单页: frontend/{table.business_name}/{table.business_name}Form.vue
- API: frontend/{table.business_name}/{table.business_name}.js

## 前端公共组件
- BaseSearch: frontend/components/BaseSearch/index.vue
- BaseTable: frontend/components/BaseTable/index.vue
- BasePagination: frontend/components/BasePagination/index.vue
- BaseForm: frontend/components/BaseForm/index.vue

## 工具函数
- timeFormatter: frontend/utils/timeFormatter.js

## 使用说明
1. 将后端文件复制到对应目录
2. 将前端文件复制到对应目录
3. **将公共组件复制到 src/components 目录**
4. **将工具函数复制到 src/utils 目录**
5. 根据实际需求调整代码
6. 测试功能是否正常
"""
            zip_file.writestr("README.md", readme_content)
        
        try:
            history = GenHistory(
                table_id=request.table_id,
                table_name=table.table_name,
                gen_type='1',
                file_count=len(code_files),
                status='1',
                create_time=datetime.now()
            )
            session.add(history)
            session.commit()
        except Exception as e:
            logger.warning(f"保存生成历史失败: {e}")
        
        zip_buffer.seek(0)
        filename = f"{table.business_name}_code_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"代码下载失败: {e}", exc_info=True)
        return respModel.error_resp(f"代码下载失败:{e}")

@module_route.post("/batchDownload", summary="批量下载代码", dependencies=[Depends(check_permission("generator:code:batchDownload"))])
async def batchDownload(request: GenerateBatchRequest, session: Session = Depends(get_session)):
    """批量下载生成的代码"""
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            for table_id in request.table_ids:
                table = session.get(GenTable, table_id)
                if not table:
                    logger.warning(f"表配置{table_id}不存在,跳过")
                    continue
                
                statement = select(GenTableColumn).where(GenTableColumn.table_id == table_id).order_by(GenTableColumn.sort)
                columns = session.exec(statement).all()
                
                if not columns:
                    logger.warning(f"表{table.table_name}字段配置不存在,跳过")
                    continue
                
                generator = ASTCodeGenerator()
                code_files = generator.generate_code(table, columns)
                
                if not code_files:
                    logger.warning(f"表{table.table_name}代码生成失败,跳过")
                    continue
                
                # 后端代码
                if 'model' in code_files:
                    zip_file.writestr(f"{table.business_name}/backend/models/{table.class_name}Model.py", code_files['model'])
                if 'schema' in code_files:
                    zip_file.writestr(f"{table.business_name}/backend/schemas/{table.class_name}Schema.py", code_files['schema'])
                if 'service' in code_files:
                    zip_file.writestr(f"{table.business_name}/backend/services/{table.class_name}Service.py", code_files['service'])
                if 'controller' in code_files:
                    zip_file.writestr(f"{table.business_name}/backend/api/{table.class_name}Controller.py", code_files['controller'])
                
                # 前端代码
                if 'list.vue' in code_files:
                    zip_file.writestr(f"{table.business_name}/frontend/{table.business_name}List.vue", code_files['list.vue'])
                if 'form.vue' in code_files:
                    zip_file.writestr(f"{table.business_name}/frontend/{table.business_name}Form.vue", code_files['form.vue'])
                if 'api.js' in code_files:
                    zip_file.writestr(f"{table.business_name}/frontend/{table.business_name}.js", code_files['api.js'])
                
                # 前端公共组件(只在第一个表时生成一次)
                if table_id == request.table_ids[0]:
                    if 'BaseSearch.vue' in code_files:
                        zip_file.writestr(f"frontend-components/BaseSearch/index.vue", code_files['BaseSearch.vue'])
                    if 'BaseTable.vue' in code_files:
                        zip_file.writestr(f"frontend-components/BaseTable/index.vue", code_files['BaseTable.vue'])
                    if 'BasePagination.vue' in code_files:
                        zip_file.writestr(f"frontend-components/BasePagination/index.vue", code_files['BasePagination.vue'])
                    if 'BaseForm.vue' in code_files:
                        zip_file.writestr(f"frontend-components/BaseForm/index.vue", code_files['BaseForm.vue'])
                    if 'timeFormatter.js' in code_files:
                        zip_file.writestr(f"frontend-utils/timeFormatter.js", code_files['timeFormatter.js'])
                
                try:
                    history = GenHistory(
                        table_id=table_id,
                        table_name=table.table_name,
                        gen_type='1',
                        file_count=len(code_files),
                        status='1',
                        create_time=datetime.now()
                    )
                    session.add(history)
                except Exception as e:
                    logger.warning(f"保存历史失败: {e}")
            
            session.commit()
        
        zip_buffer.seek(0)
        filename = f"batch_code_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        
        return StreamingResponse(
            io.BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"批量下载失败: {e}", exc_info=True)
        return respModel.error_resp(f"批量下载失败:{e}")

@module_route.get("/history", summary="获取代码生成历史", dependencies=[Depends(check_permission("generator:history:query"))])
async def getHistory(table_id: int = None, session: Session = Depends(get_session)):
    """获取代码生成历史记录"""
    try:
        statement = select(GenHistory)
        if table_id:
            statement = statement.where(GenHistory.table_id == table_id)
        
        statement = statement.order_by(GenHistory.create_time.desc()).limit(50)
        histories = session.exec(statement).all()
        
        return respModel.ok_resp_simple(lst=histories, msg="查询成功")
    except Exception as e:
        logger.error(f"查询历史失败: {e}", exc_info=True)
        return respModel.error_resp(f"查询失败:{e}")
