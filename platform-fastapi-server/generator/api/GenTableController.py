# -*- coding: utf-8 -*-
"""代码生成器-表配置管理控制器"""
from datetime import datetime

from core.database import get_session
from core.dependencies import check_permission
from core.logger import get_logger
from core.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..model.GenTable import GenTable
from ..model.GenTableColumn import GenTableColumn
from ..schemas.gen_table_schema import GenTableQuery, GenTableUpdate, GenTableImport
from ..service.DbMetaService import DbMetaService
from ..service.GenTableService import GenTableService

module_name = "GenTable" # 模块名称
module_model = GenTable
module_route = APIRouter(prefix=f"/{module_name}", tags=["代码生成器-表配置"])
logger = get_logger(__name__)

@module_route.get("/dbTables", summary="获取数据库可导入表", dependencies=[Depends(check_permission("generator:table:query"))])
async def getDbTables(session: Session = Depends(get_session)):
    """获取数据库所有表(用于导入表)"""
    try:
        db_service = DbMetaService()
        tables = db_service.get_all_tables()
        
        # 过滤已导入的表
        statement = select(GenTable.table_name)
        imported_tables = [t for t in session.exec(statement).all()]
        
        available_tables = [t for t in tables if t not in imported_tables]
        
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
        
        for table_name in request.table_names:
            # 检查是否已导入
            statement = select(GenTable).where(GenTable.table_name == table_name)
            existing = session.exec(statement).first()
            if existing:
                logger.warning(f"表{table_name}已存在,跳过")
                continue
            
            # 获取表信息
            table_info = db_service.get_table_info(table_name)
            if not table_info:
                logger.error(f"获取表{table_name}信息失败")
                continue

            # 生成类名和业务名
            class_name = ''.join(x.title() for x in table_name.split('_'))
            business_name = table_name.lower()

            # 准备表数据
            table_data = {
                'table_name': table_name,
                'table_comment': table_info.get('table_comment', ''),
                'class_name': class_name,
                'business_name': business_name,
                'function_name': table_info.get('table_comment', table_name),
                'columns': db_service.get_column_details(table_name)
            }

            tables_data_list.append(table_data)

        # 使用Service批量导入
        gen_service = GenTableService(session)
        imported_count = gen_service.batch_import_tables(tables_data_list)
        logger.info(f"批量导入表配置成功: 导入{imported_count}张表")
        return respModel.ok_resp_text(msg=f"成功导入{imported_count}张表配置")
    except Exception as e:
        session.rollback()
        logger.error(f"导入表配置失败: {e}", exc_info=True)
        return respModel.error_resp(f"导入失败:{e}")

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
        
        # 统计总数
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
        # 查询表配置
        table = session.get(GenTable, id)
        if not table:
            return respModel.error_resp("表配置不存在")
        
        # 查询字段配置
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
        # 删除表配置
        table = session.get(GenTable, id)
        if not table:
            return respModel.error_resp("表配置不存在")
        
        # 删除关联的字段配置
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
