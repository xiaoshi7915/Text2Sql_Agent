"""
添加数据源表数量和连接状态字段迁移
"""

import sqlalchemy as sa
from alembic import op

# 修订ID
revision = '9ce74f9348b4'
down_revision = '9ce74f9348b3'  # 确保这个是上一个迁移的ID
branch_labels = None
depends_on = None


def upgrade():
    """升级数据库结构"""
    op.add_column('datasources', sa.Column('table_count', sa.Integer, default=0, nullable=True))
    op.add_column('datasources', sa.Column('connection_status', sa.String(20), default='disconnected', nullable=True))

    # 为所有现有数据源设置默认值
    op.execute("UPDATE datasources SET table_count = 0, connection_status = 'disconnected'")


def downgrade():
    """降级数据库结构"""
    op.drop_column('datasources', 'table_count')
    op.drop_column('datasources', 'connection_status') 