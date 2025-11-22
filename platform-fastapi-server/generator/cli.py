# -*- coding: utf-8 -*-
"""代码生成器命令行工具"""
import os
from typing import List

import typer
from core.database import engine
from core.logger import get_logger
from generator.model.GenTable import GenTable
from generator.model.GenTableColumn import GenTableColumn
from generator.service.ASTCodeGenerator import ASTCodeGenerator
from generator.service.DbMetaService import DbMetaService
from sqlmodel import Session

logger = get_logger(__name__)
app = typer.Typer(help="代码生成器CLI工具 - 快速生成CRUD代码")


@app.command("list")
def list_tables():
    """列出数据库中所有表"""
    try:
        with Session(engine) as session:
            db_service = DbMetaService(session)
            tables = db_service.get_table_list()
            
            if not tables:
                typer.echo("❌ 未找到任何表")
                return
            
            typer.echo(f"\n✅ 找到 {len(tables)} 张表:\n")
            typer.echo("=" * 80)
            typer.echo(f"{'序号':<6} {'表名':<30} {'注释':<40}")
            typer.echo("=" * 80)
            
            for idx, table in enumerate(tables, 1):
                typer.echo(f"{idx:<6} {table['table_name']:<30} {table['table_comment'] or '-':<40}")
            
            typer.echo("=" * 80)
    except Exception as e:
        typer.echo(f"❌ 查询失败: {str(e)}", err=True)


@app.command("gen")
def generate_code(
    table: List[str] = typer.Option(..., "-t", "--table", help="表名(支持通配符/多表,如 t_user 或 -t t_user -t t_role)"),
    module: str = typer.Option("generated", "-m", "--module", help="模块名称"),
    output: str = typer.Option("./generated_code", "-o", "--output", help="输出目录"),
    preview: bool = typer.Option(False, "-p", "--preview", help="仅预览不生成文件")
):
    """生成代码(支持单表/多表/模糊匹配)
    
    示例:
        # 生成单张表
        python -m generator.cli gen -t t_user
        
        # 生成多张表
        python -m generator.cli gen -t t_user -t t_role
        或
        python -m generator.cli gen -t t_user,t_role
        
        # 模糊匹配生成
        python -m generator.cli gen -t t_%
        
        # 指定模块和输出路径
        python -m generator.cli gen -t t_user -m sysmanage -o ./output
    """
    try:
        with Session(engine) as session:
            db_service = DbMetaService(session)
            generator = ASTCodeGenerator()
            
            # 处理表名(支持逗号分隔和通配符)
            table_names = []
            for t_input in table:
                if ',' in t_input:
                    table_names.extend([t.strip() for t in t_input.split(',')])
                elif '%' in t_input:
                    # 模糊匹配
                    all_tables = db_service.get_table_list()
                    pattern = t_input.replace('%', '.*')
                    import re
                    table_names.extend([t['table_name'] for t in all_tables if re.match(pattern, t['table_name'])])
                else:
                    table_names.append(t_input)
            
            # 去重
            table_names = list(set(table_names))
            
            if not table_names:
                typer.echo("❌ 未找到匹配的表")
                return
            
            # 预扫描：获取所有关联表中的中间表
            all_link_tables = set()
            for tn in table_names:
                rels = db_service.get_relationships(tn)
                for rel in rels:
                    if rel.get('link_table'):
                        all_link_tables.add(rel['link_table'])
            
            typer.echo(f"\n🎯 准备生成 {len(table_names)} 张表的代码:")
            for tn in table_names:
                tag = " (中间表)" if tn in all_link_tables else ""
                typer.echo(f"  - {tn}{tag}")
            
            if not preview:
                confirm = typer.confirm("\n确认生成?")
                if not confirm:
                    typer.echo("❌ 已取消")
                    return
            
            # 逐表生成
            success_count = 0
            for table_name in table_names:
                try:
                    typer.echo(f"\n{'='*80}")
                    typer.echo(f"📦 正在处理: {table_name}")
                    typer.echo(f"{'='*80}")
                    
                    # 获取表结构
                    table_info = db_service.get_table_info(table_name)
                    if not table_info:
                        typer.echo(f"⚠️  表不存在: {table_name}")
                        continue
                    
                    columns = db_service.get_column_list(table_name)
                    if not columns:
                        typer.echo(f"⚠️  未找到字段: {table_name}")
                        continue
                    
                    # 智能识别表类型
                    tpl_category = 'crud'
                    # 如果是中间表，标记为 link_table
                    if table_name in all_link_tables:
                        tpl_category = 'link_table'
                        typer.echo(f"🔗 识别为中间关联表: {table_name} (只生成Model)")
                    
                    tree_code = None
                    tree_parent_code = None
                    tree_name = None
                    
                    col_names = [c['column_name'] for c in columns]
                    if 'parent_id' in col_names and tpl_category != 'link_table':
                        tpl_category = 'tree'
                        tree_code = 'id' if 'id' in col_names else col_names[0]
                        tree_parent_code = 'parent_id'
                        # 尝试猜测树名称字段
                        for name_guess in ['name', 'title', 'dept_name', 'menu_name', 'label']:
                            if name_guess in col_names:
                                tree_name = name_guess
                                break
                        if not tree_name:
                            tree_name = col_names[1] if len(col_names) > 1 else col_names[0]
                        
                        typer.echo(f"🌳 识别为树形结构表: {table_name}")

                    # 生成GenTable对象
                    # 处理表名去前缀
                    clean_table_name = table_name
                    if table_name.startswith('t_'):
                        clean_table_name = table_name[2:]
                    
                    gen_table = GenTable(
                        table_name=table_name,
                        table_comment=table_info['table_comment'] or table_name,
                        class_name=db_service._to_pascal_case(clean_table_name),
                        module_name=module,
                        business_name=db_service._to_snake_case(clean_table_name),
                        function_name=table_info['table_comment'] or table_name,
                        gen_path=output,
                        tpl_category=tpl_category,
                        tree_code=tree_code,
                        tree_parent_code=tree_parent_code,
                        tree_name=tree_name
                    )
                    
                    gen_columns = [
                        GenTableColumn(
                            table_id=0,
                            column_name=col['column_name'],
                            column_comment=col['column_comment'],
                            column_type=col['data_type'],
                            column_length=col.get('character_maximum_length'),
                            is_pk="1" if col['is_pk'] else "0",
                            is_required="1" if (col['is_nullable'] == 'NO' and not col['is_pk']) else "0",
                            is_insert="1",
                            is_edit="0" if col['is_pk'] else "1",
                            is_list="1",
                            is_query="1" if (col['is_pk'] or col['column_name'] in ['name', 'title', 'status']) else "0",
                            query_type='LIKE' if col['column_name'] in ['name', 'title'] else 'EQ',
                            python_type=db_service._map_python_type(col['data_type']),
                            python_field=col['column_name']
                        )
                        for col in columns
                    ]
                    
                    # 生成代码
                    if preview:
                        # 预览模式
                        code_files = generator.generate_code(gen_table, gen_columns, db_service)
                        for file_type, content in code_files.items():
                            typer.echo(f"\n📄 {file_type}:")
                            typer.echo("-" * 80)
                            typer.echo(content[:500] + "..." if len(content) > 500 else content)
                    else:
                        # 生成文件
                        code_files = generator.generate_code(gen_table, gen_columns, db_service)
                        
                        # 创建输出目录
                        module_path = os.path.join(output, module)
                        dirs = ["model", "schemas", "api"]
                        for d in dirs:
                            dir_path = os.path.join(module_path, d)
                            os.makedirs(dir_path, exist_ok=True)
                            # 创建__init__.py
                            init_file = os.path.join(dir_path, "__init__.py")
                            if not os.path.exists(init_file):
                                with open(init_file, 'w', encoding='utf-8') as f:
                                    f.write("")
                        
                        # 创建模块根目录__init__.py
                        root_init = os.path.join(module_path, "__init__.py")
                        if not os.path.exists(root_init):
                             with open(root_init, 'w', encoding='utf-8') as f:
                                    f.write("")
                        
                        # 写入文件
                        file_map = {
                            "model": f"model/{gen_table.class_name}Model.py",
                            "schema": f"schemas/{gen_table.class_name}Schema.py",
                            "controller": f"api/{gen_table.class_name}Controller.py"
                        }
                        
                        for file_type, file_path in file_map.items():
                            if file_type in code_files:
                                full_path = os.path.join(module_path, file_path)
                                with open(full_path, 'w', encoding='utf-8') as f:
                                    f.write(code_files[file_type])
                                typer.echo(f"✅ 已生成: {full_path}")
                        
                        success_count += 1
                
                except Exception as e:
                    typer.echo(f"❌ 生成失败: {table_name} - {str(e)}", err=True)
                    logger.error(f"生成失败: {table_name}", exc_info=True)
            
            if not preview:
                typer.echo(f"\n{'='*80}")
                typer.echo(f"🎉 生成完成! 成功: {success_count}/{len(table_names)}")
                typer.echo(f"📁 输出目录: {os.path.abspath(output)}")
                typer.echo(f"{'='*80}")
    
    except Exception as e:
        typer.echo(f"❌ 执行失败: {str(e)}", err=True)
        logger.error("CLI执行失败", exc_info=True)


@app.command("info")
def table_info(
    table: str = typer.Option(..., "-t", "--table", help="表名")
):
    """查看表详细信息"""
    try:
        with Session(engine) as session:
            db_service = DbMetaService(session)
            
            # 获取表信息
            table_info = db_service.get_table_info(table)
            if not table_info:
                typer.echo(f"❌ 表不存在: {table}")
                return
            
            # 获取字段信息
            columns = db_service.get_column_list(table)
            
            typer.echo(f"\n📋 表信息: {table}")
            typer.echo("=" * 80)
            typer.echo(f"表名: {table_info['table_name']}")
            typer.echo(f"注释: {table_info['table_comment'] or '-'}")
            typer.echo(f"字段数: {len(columns)}")
            
            typer.echo(f"\n📊 字段列表:")
            typer.echo("=" * 80)
            typer.echo(f"{'字段名':<20} {'类型':<15} {'主键':<6} {'必填':<6} {'注释':<30}")
            typer.echo("=" * 80)
            
            for col in columns:
                is_pk = '✓' if col['is_pk'] else ''
                is_required = '✓' if col['is_nullable'] == 'NO' else ''
                typer.echo(
                    f"{col['column_name']:<20} "
                    f"{col['data_type']:<15} "
                    f"{is_pk:<6} "
                    f"{is_required:<6} "
                    f"{col['column_comment'] or '-':<30}"
                )
            
            typer.echo("=" * 80)
    
    except Exception as e:
        typer.echo(f"❌ 查询失败: {str(e)}", err=True)


if __name__ == "__main__":
    app()
