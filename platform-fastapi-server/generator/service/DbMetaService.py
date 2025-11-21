# -*- coding: utf-8 -*-
"""数据库元数据解析服务"""
from sqlalchemy import create_engine, inspect, text
from typing import List, Dict, Optional
from config.dev_settings import settings
from core.logger import get_logger

logger = get_logger(__name__)

class DbMetaService:
    """数据库元数据解析服务 - 反向工程核心"""
    
    def __init__(self, session=None):
        """初始化数据库元数据服务
        
        Args:
            session: SQLModel Session对象(可选,主要用于Web API调用)
        """
        self.session = session
        self.engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        self.inspector = inspect(self.engine)
    
    def get_all_tables(self) -> List[str]: # 获取所有表名
        """获取数据库所有表名列表"""
        try:
            tables = self.inspector.get_table_names()
            logger.info(f"获取到{len(tables)}张表")
            return tables
        except Exception as e:
            logger.error(f"获取表列表失败: {e}")
            return []
    
    def get_table_list(self) -> List[Dict]: # 获取表列表(含注释)
        """获取数据库所有表的详细信息列表
        
        Returns:
            List[Dict]: 包含表名和注释的字典列表
        """
        try:
            tables = self.inspector.get_table_names()
            table_list = []
            for table_name in tables:
                table_comment = self._get_table_comment(table_name)
                table_list.append({
                    'table_name': table_name,
                    'table_comment': table_comment or ''
                })
            logger.info(f"获取到{len(table_list)}张表的详细信息")
            return table_list
        except Exception as e:
            logger.error(f"获取表列表失败: {e}")
            return []
    
    def get_column_list(self, table_name: str) -> List[Dict]: # 获取字段列表
        """获取指定表的字段列表(含注释和详细信息)
        
        Args:
            table_name: 表名
            
        Returns:
            List[Dict]: 字段详细信息列表
        """
        try:
            columns = self.inspector.get_columns(table_name)
            pk_columns = self.inspector.get_pk_constraint(table_name).get('constrained_columns', [])
            
            column_list = []
            for col in columns:
                column_name = col['name']
                column_comment = self._get_column_comment(table_name, column_name)
                
                column_list.append({
                    'column_name': column_name,
                    'column_comment': column_comment or column_name,
                    'data_type': str(col['type']),
                    'is_nullable': 'YES' if col.get('nullable', True) else 'NO',
                    'is_pk': column_name in pk_columns,
                    'character_maximum_length': col.get('type').length if hasattr(col.get('type'), 'length') else None
                })
            
            logger.info(f"获取表{table_name}的{len(column_list)}个字段")
            return column_list
        except Exception as e:
            logger.error(f"获取字段列表失败: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Optional[Dict]: # 获取表详细信息
        try:
            # 获取表注释
            table_comment = self._get_table_comment(table_name)
            
            # 获取列信息
            columns = self.inspector.get_columns(table_name)
            
            # 获取主键
            pk_constraint = self.inspector.get_pk_constraint(table_name)
            pk_columns = pk_constraint.get('constrained_columns', [])
            
            # 获取索引
            indexes = self.inspector.get_indexes(table_name)
            
            # 获取外键
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            
            return {
                'table_name': table_name,
                'table_comment': table_comment or '',
                'columns': columns,
                'primary_keys': pk_columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys
            }
        except Exception as e:
            logger.error(f"获取表{table_name}信息失败: {e}")
            return None
    
    def _get_table_comment(self, table_name: str) -> Optional[str]: # 获取表注释
        try:
            with self.engine.connect() as conn:
                if settings.DB_TYPE.lower() == 'mysql':
                    sql = text(f"""
                        SELECT TABLE_COMMENT 
                        FROM information_schema.TABLES 
                        WHERE TABLE_SCHEMA = '{settings.MYSQL_DATABASE}' 
                        AND TABLE_NAME = '{table_name}'
                    """)
                    result = conn.execute(sql).fetchone()
                    return result[0] if result else None
                else: # SQLite不支持表注释
                    return None
        except Exception as e:
            logger.warning(f"获取表注释失败: {e}")
            return None
    
    def get_column_details(self, table_name: str) -> List[Dict]: # 获取表字段详细信息(含注释)
        try:
            columns = self.inspector.get_columns(table_name)
            pk_columns = self.inspector.get_pk_constraint(table_name).get('constrained_columns', [])
            
            column_details = []
            for idx, col in enumerate(columns):
                column_name = col['name']
                column_type = str(col['type'])
                
                # 获取字段注释
                column_comment = self._get_column_comment(table_name, column_name)
                
                # 判断是否主键
                is_pk = '1' if column_name in pk_columns else '0'
                
                # 判断是否自增
                is_increment = '1' if col.get('autoincrement', False) else '0'
                
                # 判断是否必填
                is_required = '0' if col.get('nullable', True) else '1'
                
                # Python类型映射
                python_type = self._map_python_type(column_type)
                
                # Python字段名(驼峰命名)
                python_field = self._to_camel_case(column_name)
                
                column_details.append({
                    'column_name': column_name,
                    'column_comment': column_comment or column_name,
                    'column_type': column_type,
                    'python_type': python_type,
                    'python_field': python_field,
                    'is_pk': is_pk,
                    'is_increment': is_increment,
                    'is_required': is_required,
                    'sort': idx + 1
                })
            
            return column_details
        except Exception as e:
            logger.error(f"获取表{table_name}字段详情失败: {e}")
            return []

    def get_relationships(self, table_name: str) -> List[Dict]:
        """获取表的多对多关联关系
        
        支持两种模式：
        1. 物理外键探测
        2. 命名约定探测 (软关联): 寻找包含 {table}_id 和 {other}_id 的中间表
        """
        relationships = []
        try:
            all_tables = self.inspector.get_table_names()
            
            #以此表名为基准寻找关联
            # 假设当前表是 t_user, 寻找 t_user_role 或 user_role 这样的表
            # 或者寻找包含 user_id 的表
            
            current_id_col = f"{table_name[2:] if table_name.startswith('t_') else table_name}_id"
            
            for other_table in all_tables:
                if other_table == table_name:
                    continue
                
                # 策略1: 物理外键 (现有逻辑)
                fks = self.inspector.get_foreign_keys(other_table)
                has_fk_match = False
                target_table_fk = None
                
                if fks:
                    current_fk_found = False
                    for fk in fks:
                        if fk['referred_table'] == table_name:
                            current_fk_found = True
                        else:
                            target_table_fk = fk['referred_table']
                    
                    if current_fk_found and target_table_fk and len(fks) >= 2:
                        has_fk_match = True

                # 策略2: 命名约定 (软关联)
                # 如果表名包含当前表名 (例如 t_user_role 包含 user)
                # 并且包含 current_id_col (user_id)
                # 并且包含另一个 x_id
                
                columns = self.inspector.get_columns(other_table)
                col_names = [c['name'] for c in columns]
                
                has_soft_match = False
                target_table_soft = None
                
                if current_id_col in col_names:
                    # 寻找另一个 _id 字段
                    for col in col_names:
                        if col != current_id_col and col.endswith('_id') and col != 'parent_id':
                            # 猜测目标表名: role_id -> t_role
                            guess_target = f"t_{col[:-3]}"
                            if guess_target in all_tables:
                                target_table_soft = guess_target
                                has_soft_match = True
                                break
                            # 尝试不带t_的情况
                            if col[:-3] in all_tables:
                                target_table_soft = col[:-3]
                                has_soft_match = True
                                break

                # 综合判定
                if has_fk_match:
                    target_table = target_table_fk
                elif has_soft_match:
                    target_table = target_table_soft
                else:
                    continue

                # 生成关联信息
                if target_table:
                    target_clean_name = target_table[2:] if target_table.startswith('t_') else target_table
                    
                    # 避免重复添加
                    exists = any(r['target_table'] == target_table for r in relationships)
                    if not exists:
                        rel = {
                            'type': 'ManyToMany',
                            'target_table': target_table,
                            'target_model': self._to_pascal_case(target_clean_name),
                            'link_table': other_table,
                            'link_model': self._to_pascal_case(other_table[2:] if other_table.startswith('t_') else other_table),
                            'field_name': self._to_snake_case(target_clean_name) + 's', # 简单复数化
                            'back_populates': self._to_snake_case(table_name[2:] if table_name.startswith('t_') else table_name) + 's'
                        }
                        relationships.append(rel)
                        logger.info(f"🔗 发现关联关系: {table_name} <-> {target_table} (via {other_table})")
            
            return relationships
        except Exception as e:
            logger.error(f"探测关联关系失败: {e}")
            return []
    
    def _get_column_comment(self, table_name: str, column_name: str) -> Optional[str]: # 获取字段注释
        try:
            with self.engine.connect() as conn:
                if settings.DB_TYPE.lower() == 'mysql':
                    sql = text(f"""
                        SELECT COLUMN_COMMENT 
                        FROM information_schema.COLUMNS 
                        WHERE TABLE_SCHEMA = '{settings.MYSQL_DATABASE}' 
                        AND TABLE_NAME = '{table_name}' 
                        AND COLUMN_NAME = '{column_name}'
                    """)
                    result = conn.execute(sql).fetchone()
                    return result[0] if result else None
                else: # SQLite不支持字段注释
                    return None
        except Exception as e:
            logger.warning(f"获取字段注释失败: {e}")
            return None
    
    def _map_python_type(self, db_type: str) -> str: # 数据库类型映射到Python类型
        db_type = db_type.upper()
        
        # 整数类型
        if any(t in db_type for t in ['INT', 'INTEGER', 'BIGINT', 'SMALLINT']):
            return 'int'
        # 浮点类型
        elif any(t in db_type for t in ['FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC']):
            return 'float'
        # 布尔类型
        elif 'BOOL' in db_type:
            return 'bool'
        # 日期时间类型
        elif any(t in db_type for t in ['DATETIME', 'TIMESTAMP']):
            return 'datetime'
        elif 'DATE' in db_type:
            return 'date'
        elif 'TIME' in db_type:
            return 'time'
        # 文本类型
        elif any(t in db_type for t in ['TEXT', 'CLOB', 'JSON']):
            return 'str'
        # 默认字符串类型
        else:
            return 'str'
    
    def _to_camel_case(self, snake_str: str) -> str: # 下划线转驼峰命名
        """下划线命名转驼峰命名(首字母小写)
        
        Args:
            snake_str: 下划线命名字符串
            
        Returns:
            str: 驼峰命名字符串
        """
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def _to_pascal_case(self, snake_str: str) -> str: # 下划线转帕斯卡命名(首字母大写)
        """下划线命名转帕斯卡命名(首字母大写)
        
        Args:
            snake_str: 下划线命名字符串
            
        Returns:
            str: 帕斯卡命名字符串
        """
        return ''.join(x.title() for x in snake_str.split('_'))
    
    def _to_snake_case(self, text: str) -> str: # 转下划线命名
        """将字符串转换为下划线命名
        
        Args:
            text: 原始字符串
            
        Returns:
            str: 下划线命名字符串
        """
        import re
        # 处理帕斯卡命名或驼峰命名
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
