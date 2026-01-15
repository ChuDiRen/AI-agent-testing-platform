# -*- coding: utf-8 -*-
"""代码生成器-表配置管理控制器"""
from datetime import datetime

from app.database.database import get_session
from app.dependencies.dependencies import check_permission
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlmodel import Session, select

from app.models.GenTable import GenTable
from app.models.GenTableColumn import GenTableColumn
from app.schemas.GenTableSchema import GenTableQuery, GenTableUpdate, GenTableImport
from app.services.DbMetaService import DbMetaService
from app.services.GenTableService import GenTableService
from app.services.SqlParserService import SqlParserService

module_name = "GenTable"
module_model = GenTable
module_route = APIRouter(prefix=f"/{module_name}", tags=["代码生成器-表配置"])
logger = get_logger(__name__)

@module_route.get("/dbTables", summary="获取数据库可导入表", dependencies=[Depends(check_permission("generator:table:query"))])
async def getDbTables(session: Session = Depends(get_session)):
    """获取数据库所有表(用于导入表)"""
    try:
        db_service = DbMetaService()
        # 获取表列表(含表名和注释)
        tables = db_service.get_table_list()
        
        # 获取已导入的表名
        statement = select(GenTable.table_name)
        imported_tables = [t for t in session.exec(statement).all()]
        
        # 过滤已导入的表，返回对象列表
        available_tables = [t for t in tables if t['table_name'] not in imported_tables]
        
        return respModel.ok_resp_simple(lst=available_tables, msg=f"获取到{len(available_tables)}张可导入的表")
    except Exception as e:
        logger.error(f"获取数据库表列表失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误:{e}")

@module_route.post("/importTables", summary="批量导入表配置", dependencies=[Depends(check_permission("generator:table:import"))])
async def importTables(request: GenTableImport, session: Session = Depends(get_session)):
    """批量导入表配置"""
    try:
        db_service = DbMetaService()
        imported_count = 0
        
        tables_data_list = []
        
        for table_name in request.table_names:
            statement = select(GenTable).where(GenTable.table_name == table_name)
            existing = session.exec(statement).first()
            if existing:
                logger.warning(f"表{table_name}已存在,跳过")
                continue
            
            table_info = db_service.get_table_info(table_name)
            if not table_info:
                logger.error(f"获取表{table_name}信息失败")
                continue

            class_name = ''.join(x.title() for x in table_name.split('_'))
            business_name = table_name.lower()

            table_data = {
                'table_name': table_name,
                'table_comment': table_info.get('table_comment', ''),
                'class_name': class_name,
                'business_name': business_name,
                'function_name': table_info.get('table_comment', table_name),
                'columns': db_service.get_column_details(table_name)
            }

            tables_data_list.append(table_data)

        gen_service = GenTableService(session)
        imported_count = gen_service.batch_import_tables(tables_data_list)
        logger.info(f"批量导入表配置成功: 导入{imported_count}张表")
        return respModel.ok_resp_text(msg=f"成功导入{imported_count}张表配置")
    except Exception as e:
        session.rollback()
        logger.error(f"导入表配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"导入失败:{e}")


@module_route.post("/uploadSql", summary="上传SQL文件导入表配置", dependencies=[Depends(check_permission("generator:table:import"))])
async def uploadSqlFile(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    上传 SQL 文件，解析 CREATE TABLE 语句并导入表配置
    支持 .sql 文件，自动解析 DDL 语句
    """
    try:
        # 验证文件类型
        if not file.filename.endswith('.sql'):
            return respModel.error_resp("只支持 .sql 文件")
        
        # 读取文件内容
        content = await file.read()
        
        # 尝试多种编码解析
        sql_content = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                sql_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if sql_content is None:
            return respModel.error_resp("无法解析文件编码，请使用 UTF-8 编码")
        
        # 解析 SQL 文件
        parser = SqlParserService()
        tables_data = parser.parse_sql_file(sql_content)
        
        if not tables_data:
            return respModel.error_resp("未能从 SQL 文件中解析到任何表结构")
        
        # 过滤已存在的表
        tables_to_import = []
        skipped_tables = []
        
        for table_data in tables_data:
            table_name = table_data['table_name']
            statement = select(GenTable).where(GenTable.table_name == table_name)
            existing = session.exec(statement).first()
            
            if existing:
                skipped_tables.append(table_name)
                logger.warning(f"表 {table_name} 已存在，跳过")
            else:
                tables_to_import.append(table_data)
        
        if not tables_to_import:
            return respModel.error_resp(f"所有表都已存在: {', '.join(skipped_tables)}")
        
        # 批量导入
        gen_service = GenTableService(session)
        imported_count = gen_service.batch_import_tables(tables_to_import)
        
        msg = f"成功导入 {imported_count} 张表"
        if skipped_tables:
            msg += f"，跳过已存在的表: {', '.join(skipped_tables)}"
        
        logger.info(f"SQL文件导入完成: {msg}")
        return respModel.ok_resp(data=imported_count, msg=msg)
        
    except Exception as e:
        session.rollback()
        logger.error(f"上传SQL文件失败: {e}", exc_info=True)
        return respModel.error_resp(f"导入失败: {e}")

@module_route.post("/queryByPage", summary="分页查询表配置", dependencies=[Depends(check_permission("generator:table:query"))])
async def queryByPage(query: GenTableQuery, session: Session = Depends(get_session)):
    try:
        offset = (query.page - 1) * query.pageSize
        statement = select(module_model)
        
        if query.table_name:
            statement = statement.where(module_model.table_name.like(f"%{query.table_name}%"))
        if query.table_comment:
            statement = statement.where(module_model.table_comment.like(f"%{query.table_comment}%"))
        
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        count_statement = select(module_model)
        if query.table_name:
            count_statement = count_statement.where(module_model.table_name.like(f"%{query.table_name}%"))
        if query.table_comment:
            count_statement = count_statement.where(module_model.table_comment.like(f"%{query.table_comment}%"))
        total = len(session.exec(count_statement).all())
        
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.get("/queryById", summary="根据ID查询表配置", dependencies=[Depends(check_permission("generator:table:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        table = session.get(GenTable, id)
        if not table:
            return respModel.error_resp("表配置不存在")
        
        statement = select(GenTableColumn).where(GenTableColumn.table_id == id).order_by(GenTableColumn.sort)
        columns = session.exec(statement).all()
        
        result = {
            "table": table,
            "columns": columns
        }
        return respModel.ok_resp(obj=result)
    except Exception as e:
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@module_route.put("/update", summary="更新表配置", dependencies=[Depends(check_permission("generator:table:edit"))])
async def update(data: GenTableUpdate, session: Session = Depends(get_session)):
    try:
        table = session.get(GenTable, data.id)
        if not table:
            return respModel.error_resp("表配置不存在")
        
        update_data = data.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(table, key, value)
        
        table.update_time = datetime.now()
        session.commit()
        
        return respModel.ok_resp(msg="修改成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败:{e}")

@module_route.delete("/delete", summary="删除表配置", dependencies=[Depends(check_permission("generator:table:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    try:
        table = session.get(GenTable, id)
        if not table:
            return respModel.error_resp("表配置不存在")
        
        statement = select(GenTableColumn).where(GenTableColumn.table_id == id)
        columns = session.exec(statement).all()
        for col in columns:
            session.delete(col)
        
        session.delete(table)
        session.commit()
        
        return respModel.ok_resp(msg="删除成功")
    except Exception as e:
        session.rollback()
        logger.error(f"操作失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"删除失败:{e}")
