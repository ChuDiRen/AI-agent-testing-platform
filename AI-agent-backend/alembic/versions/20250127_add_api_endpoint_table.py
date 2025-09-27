"""add_api_endpoint_table

Revision ID: 20250127_add_api_endpoint_table
Revises: 2677b812dced
Create Date: 2025-01-27 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '20250127_add_api_endpoint_table'
down_revision = '2677b812dced'
branch_labels = None
depends_on = None


def upgrade():
    """
    创建API端点表
    """
    # 创建api_endpoint表
    op.create_table('api_endpoint',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('path', sa.String(length=500), nullable=False, comment='API路径'),
        sa.Column('method', sa.String(length=10), nullable=False, comment='HTTP方法'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='API名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='API描述'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='API状态'),
        sa.Column('module', sa.String(length=100), nullable=True, comment='所属模块'),
        sa.Column('permission', sa.String(length=100), nullable=True, comment='权限标识'),
        sa.Column('version', sa.String(length=20), nullable=True, comment='API版本'),
        sa.Column('request_example', sa.JSON(), nullable=True, comment='请求参数示例'),
        sa.Column('response_example', sa.JSON(), nullable=True, comment='响应示例'),
        sa.Column('total_calls', sa.Integer(), nullable=True, comment='总调用次数'),
        sa.Column('success_calls', sa.Integer(), nullable=True, comment='成功调用次数'),
        sa.Column('error_calls', sa.Integer(), nullable=True, comment='错误调用次数'),
        sa.Column('avg_response_time', sa.Float(), nullable=True, comment='平均响应时间(ms)'),
        sa.Column('max_response_time', sa.Float(), nullable=True, comment='最大响应时间(ms)'),
        sa.Column('min_response_time', sa.Float(), nullable=True, comment='最小响应时间(ms)'),
        sa.Column('last_called_at', sa.DateTime(), nullable=True, comment='最后调用时间'),
        sa.Column('created_by_id', sa.Integer(), nullable=False, comment='创建者ID'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='API端点表'
    )
    
    # 创建索引
    op.create_index('idx_api_endpoint_path_method', 'api_endpoint', ['path', 'method'], unique=True)
    op.create_index('idx_api_endpoint_status', 'api_endpoint', ['status'])
    op.create_index('idx_api_endpoint_module', 'api_endpoint', ['module'])
    op.create_index('idx_api_endpoint_permission', 'api_endpoint', ['permission'])
    op.create_index('idx_api_endpoint_created_by', 'api_endpoint', ['created_by_id'])
    op.create_index('idx_api_endpoint_created_at', 'api_endpoint', ['created_at'])


def downgrade():
    """
    删除API端点表
    """
    # 删除索引
    op.drop_index('idx_api_endpoint_created_at', table_name='api_endpoint')
    op.drop_index('idx_api_endpoint_created_by', table_name='api_endpoint')
    op.drop_index('idx_api_endpoint_permission', table_name='api_endpoint')
    op.drop_index('idx_api_endpoint_module', table_name='api_endpoint')
    op.drop_index('idx_api_endpoint_status', table_name='api_endpoint')
    op.drop_index('idx_api_endpoint_path_method', table_name='api_endpoint')
    
    # 删除表
    op.drop_table('api_endpoint')
