"""初始化所有表

Revision ID: 9ce74f9348b3
Revises: 
Create Date: 2025-04-24 16:53:06.493081

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9ce74f9348b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### 注释掉删除users表的部分，表已经存在 ###
    # with op.batch_alter_table('users', schema=None) as batch_op:
    #     batch_op.drop_index('email')
    #     batch_op.drop_index('username')
    # op.drop_table('users')
    
    # 创建models表
    op.create_table('models',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('model_type', sa.String(length=50), nullable=False),
    sa.Column('api_base', sa.String(length=255), nullable=True),
    sa.Column('api_key', sa.String(length=255), nullable=True),
    sa.Column('api_version', sa.String(length=50), nullable=True),
    sa.Column('temperature', sa.Float(), nullable=True),
    sa.Column('max_tokens', sa.Integer(), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('parameters', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # 创建datasources表
    op.create_table('datasources',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('ds_type', sa.String(length=50), nullable=False),
    sa.Column('host', sa.String(length=255), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('database', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('include_views', sa.Boolean(), nullable=True),
    sa.Column('format', sa.String(length=50), nullable=True),
    sa.Column('selected_fields', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # 创建conversations表
    op.create_table('conversations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('model_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['model_id'], ['models.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # 创建conversation_datasources关联表
    op.create_table('conversation_datasources',
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('datasource_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['datasource_id'], ['datasources.id'], ),
    sa.PrimaryKeyConstraint('conversation_id', 'datasource_id')
    )
    
    # 创建messages表
    op.create_table('messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sql_query', sa.Text(), nullable=True),
    sa.Column('query_results', sa.JSON(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('tokens_used', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('messages')
    op.drop_table('conversation_datasources')
    op.drop_table('conversations')
    op.drop_table('datasources')
    op.drop_table('models')
    
    # 注释掉恢复users表的代码
    # op.create_table('users',
    # sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    # sa.Column('username', mysql.VARCHAR(collation='utf8mb4_general_ci', length=64), nullable=False),
    # sa.Column('email', mysql.VARCHAR(collation='utf8mb4_general_ci', length=120), nullable=True),
    # sa.Column('password_hash', mysql.VARCHAR(collation='utf8mb4_general_ci', length=128), nullable=False),
    # sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    # sa.Column('is_admin', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    # sa.Column('last_login', mysql.DATETIME(), nullable=True),
    # sa.Column('created_at', mysql.DATETIME(), nullable=True),
    # sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    # sa.PrimaryKeyConstraint('id'),
    # mysql_collate='utf8mb4_general_ci',
    # mysql_default_charset='utf8mb4',
    # mysql_engine='InnoDB'
    # )
    # with op.batch_alter_table('users', schema=None) as batch_op:
    #     batch_op.create_index('username', ['username'], unique=True)
    #     batch_op.create_index('email', ['email'], unique=True)
    # ### end Alembic commands ###
