"""
代码生成表配置Service
处理表和字段的导入
"""
from datetime import datetime
from typing import List, Dict
from sqlmodel import Session

from generator.model.GenTable import GenTable
from generator.model.GenTableColumn import GenTableColumn


class GenTableService:
    def __init__(self, session: Session):
        self.session = session

    def create_table_with_columns(
        self,
        table_name: str,
        table_comment: str,
        class_name: str,
        business_name: str,
        function_name: str,
        columns: List[Dict]
    ) -> GenTable:
        """创建表配置及其字段"""
        # 创建表配置
        gen_table = GenTable(
            table_name=table_name,
            table_comment=table_comment,
            class_name=class_name,
            module_name='generator',
            business_name=business_name,
            function_name=function_name,
            create_time=datetime.now()
        )
        self.session.add(gen_table)
        self.session.flush()  # 获取gen_table.id

        # 创建字段配置
        for col in columns:
            gen_column = GenTableColumn(
                table_id=gen_table.id,
                **col,
                create_time=datetime.now()
            )
            self.session.add(gen_column)

        self.session.commit()
        return gen_table

    def batch_import_tables(
        self,
        tables_data: List[Dict]
    ) -> int:
        """批量导入表配置"""
        imported_count = 0
        for table_data in tables_data:
            try:
                self.create_table_with_columns(**table_data)
                imported_count += 1
            except Exception as e:
                logger.warning(f"导入表{table_data.get('table_name')}失败: {e}")
                continue

        return imported_count
