"""Add audit log and permission cache tables

Revision ID: 0001
Revises: 
Create Date: 2025-08-24 09:55:32.714857

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建审计日志表
    op.create_table(
        't_audit_log',
        sa.Column('LOG_ID', sa.Integer(), primary_key=True, autoincrement=True, comment='日志ID'),
        sa.Column('USER_ID', sa.Integer(), nullable=True, comment='操作用户ID'),
        sa.Column('USERNAME', sa.String(50), nullable=True, comment='操作用户名'),
        sa.Column('OPERATION_TYPE', sa.String(50), nullable=False, comment='操作类型(CREATE/UPDATE/DELETE/LOGIN/LOGOUT)'),
        sa.Column('RESOURCE_TYPE', sa.String(50), nullable=False, comment='资源类型(USER/ROLE/MENU/DEPT)'),
        sa.Column('RESOURCE_ID', sa.String(100), nullable=True, comment='资源ID'),
        sa.Column('RESOURCE_NAME', sa.String(200), nullable=True, comment='资源名称'),
        sa.Column('OPERATION_DESC', sa.String(500), nullable=True, comment='操作描述'),
        sa.Column('REQUEST_METHOD', sa.String(10), nullable=True, comment='请求方法(GET/POST/PUT/DELETE)'),
        sa.Column('REQUEST_URL', sa.String(500), nullable=True, comment='请求URL'),
        sa.Column('REQUEST_PARAMS', sa.Text(), nullable=True, comment='请求参数(JSON格式)'),
        sa.Column('RESPONSE_STATUS', sa.Integer(), nullable=True, comment='响应状态码'),
        sa.Column('RESPONSE_MESSAGE', sa.Text(), nullable=True, comment='响应消息'),
        sa.Column('IP_ADDRESS', sa.String(50), nullable=True, comment='客户端IP地址'),
        sa.Column('USER_AGENT', sa.String(500), nullable=True, comment='用户代理'),
        sa.Column('EXECUTION_TIME', sa.Integer(), nullable=True, comment='执行时间(毫秒)'),
        sa.Column('OPERATION_TIME', sa.DateTime(), default=datetime.utcnow, nullable=False, comment='操作时间'),
        sa.Column('IS_SUCCESS', sa.Integer(), default=1, comment='是否成功(0:失败,1:成功)'),
        sa.Column('ERROR_MESSAGE', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('BEFORE_DATA', sa.Text(), nullable=True, comment='操作前数据(JSON格式)'),
        sa.Column('AFTER_DATA', sa.Text(), nullable=True, comment='操作后数据(JSON格式)'),
        # 基础字段
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, comment='更新时间'),
        sa.Column('created_by', sa.String(50), comment='创建者'),
        sa.Column('updated_by', sa.String(50), comment='更新者'),
        sa.Column('is_deleted', sa.Integer(), default=0, comment='是否删除(0:未删除,1:已删除)'),
        comment='审计日志表'
    )
    
    # 创建审计日志表索引
    op.create_index('idx_audit_user_id', 't_audit_log', ['USER_ID'])
    op.create_index('idx_audit_operation_type', 't_audit_log', ['OPERATION_TYPE'])
    op.create_index('idx_audit_resource_type', 't_audit_log', ['RESOURCE_TYPE'])
    op.create_index('idx_audit_operation_time', 't_audit_log', ['OPERATION_TIME'])
    op.create_index('idx_audit_ip_address', 't_audit_log', ['IP_ADDRESS'])
    op.create_index('idx_audit_is_success', 't_audit_log', ['IS_SUCCESS'])

    # 创建权限缓存配置表
    op.create_table(
        't_permission_cache',
        sa.Column('CACHE_ID', sa.Integer(), primary_key=True, autoincrement=True, comment='缓存配置ID'),
        sa.Column('CACHE_KEY', sa.String(200), nullable=False, unique=True, comment='缓存键名'),
        sa.Column('CACHE_TYPE', sa.String(50), nullable=False, comment='缓存类型(USER_PERMISSION/ROLE_PERMISSION/MENU_TREE)'),
        sa.Column('CACHE_VALUE', sa.Text(), nullable=True, comment='缓存值(JSON格式)'),
        sa.Column('EXPIRE_TIME', sa.Integer(), default=3600, comment='过期时间(秒)'),
        sa.Column('LAST_UPDATE_TIME', sa.DateTime(), default=datetime.utcnow, comment='最后更新时间'),
        sa.Column('UPDATE_COUNT', sa.Integer(), default=0, comment='更新次数'),
        sa.Column('HIT_COUNT', sa.Integer(), default=0, comment='命中次数'),
        sa.Column('MISS_COUNT', sa.Integer(), default=0, comment='未命中次数'),
        sa.Column('IS_ACTIVE', sa.Integer(), default=1, comment='是否启用(0:禁用,1:启用)'),
        sa.Column('DESCRIPTION', sa.String(500), nullable=True, comment='缓存描述'),
        # 基础字段
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, comment='更新时间'),
        sa.Column('created_by', sa.String(50), comment='创建者'),
        sa.Column('updated_by', sa.String(50), comment='更新者'),
        sa.Column('is_deleted', sa.Integer(), default=0, comment='是否删除(0:未删除,1:已删除)'),
        comment='权限缓存配置表'
    )
    
    # 创建权限缓存表索引
    op.create_index('idx_cache_key', 't_permission_cache', ['CACHE_KEY'])
    op.create_index('idx_cache_type', 't_permission_cache', ['CACHE_TYPE'])
    op.create_index('idx_cache_active', 't_permission_cache', ['IS_ACTIVE'])
    op.create_index('idx_cache_update_time', 't_permission_cache', ['LAST_UPDATE_TIME'])

    # 创建数据权限规则表
    op.create_table(
        't_data_permission_rule',
        sa.Column('RULE_ID', sa.Integer(), primary_key=True, autoincrement=True, comment='规则ID'),
        sa.Column('RULE_NAME', sa.String(100), nullable=False, comment='规则名称'),
        sa.Column('RULE_CODE', sa.String(50), nullable=False, unique=True, comment='规则代码'),
        sa.Column('RESOURCE_TYPE', sa.String(50), nullable=False, comment='资源类型(USER/ROLE/DEPT/MENU)'),
        sa.Column('PERMISSION_TYPE', sa.String(20), nullable=False, comment='权限类型(ALL/DEPT/SELF/CUSTOM)'),
        sa.Column('RULE_EXPRESSION', sa.Text(), nullable=True, comment='规则表达式(SQL WHERE条件)'),
        sa.Column('DEPT_IDS', sa.String(500), nullable=True, comment='部门ID列表(逗号分隔)'),
        sa.Column('ROLE_IDS', sa.String(500), nullable=True, comment='角色ID列表(逗号分隔)'),
        sa.Column('USER_IDS', sa.String(500), nullable=True, comment='用户ID列表(逗号分隔)'),
        sa.Column('IS_ACTIVE', sa.Integer(), default=1, comment='是否启用(0:禁用,1:启用)'),
        sa.Column('PRIORITY', sa.Integer(), default=0, comment='优先级(数字越大优先级越高)'),
        sa.Column('DESCRIPTION', sa.String(500), nullable=True, comment='规则描述'),
        # 基础字段
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, comment='更新时间'),
        sa.Column('created_by', sa.String(50), comment='创建者'),
        sa.Column('updated_by', sa.String(50), comment='更新者'),
        sa.Column('is_deleted', sa.Integer(), default=0, comment='是否删除(0:未删除,1:已删除)'),
        comment='数据权限规则表'
    )
    
    # 创建数据权限规则表索引
    op.create_index('idx_rule_code', 't_data_permission_rule', ['RULE_CODE'])
    op.create_index('idx_rule_resource_type', 't_data_permission_rule', ['RESOURCE_TYPE'])
    op.create_index('idx_rule_permission_type', 't_data_permission_rule', ['PERMISSION_TYPE'])
    op.create_index('idx_rule_active', 't_data_permission_rule', ['IS_ACTIVE'])
    op.create_index('idx_rule_priority', 't_data_permission_rule', ['PRIORITY'])


def downgrade() -> None:
    # 删除数据权限规则表
    op.drop_index('idx_rule_priority', table_name='t_data_permission_rule')
    op.drop_index('idx_rule_active', table_name='t_data_permission_rule')
    op.drop_index('idx_rule_permission_type', table_name='t_data_permission_rule')
    op.drop_index('idx_rule_resource_type', table_name='t_data_permission_rule')
    op.drop_index('idx_rule_code', table_name='t_data_permission_rule')
    op.drop_table('t_data_permission_rule')
    
    # 删除权限缓存配置表
    op.drop_index('idx_cache_update_time', table_name='t_permission_cache')
    op.drop_index('idx_cache_active', table_name='t_permission_cache')
    op.drop_index('idx_cache_type', table_name='t_permission_cache')
    op.drop_index('idx_cache_key', table_name='t_permission_cache')
    op.drop_table('t_permission_cache')
    
    # 删除审计日志表
    op.drop_index('idx_audit_is_success', table_name='t_audit_log')
    op.drop_index('idx_audit_ip_address', table_name='t_audit_log')
    op.drop_index('idx_audit_operation_time', table_name='t_audit_log')
    op.drop_index('idx_audit_resource_type', table_name='t_audit_log')
    op.drop_index('idx_audit_operation_type', table_name='t_audit_log')
    op.drop_index('idx_audit_user_id', table_name='t_audit_log')
    op.drop_table('t_audit_log')