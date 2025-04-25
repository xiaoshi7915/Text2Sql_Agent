from datetime import datetime
from . import db
from sqlalchemy.dialects.mysql import JSON

class DataSource(db.Model):
    """数据源模型，用于存储连接各类数据库的配置信息"""
    
    __tablename__ = 'datasources'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='数据源名称')
    description = db.Column(db.Text, nullable=True, comment='描述信息')
    ds_type = db.Column(db.String(50), nullable=False, comment='数据源类型')
    host = db.Column(db.String(255), nullable=False, comment='服务器主机名/地址')
    port = db.Column(db.Integer, nullable=False, comment='端口号')
    database = db.Column(db.String(100), nullable=False, comment='数据库名称')
    username = db.Column(db.String(100), nullable=False, comment='用户名')
    password = db.Column(db.String(255), nullable=False, comment='密码(加密存储)')
    options = db.Column(JSON, nullable=True, comment='其他连接选项')
    include_views = db.Column(db.Boolean, default=False, comment='是否包含视图')
    format = db.Column(db.String(50), default='public', comment='模式名称')
    selected_fields = db.Column(db.Text, nullable=True, comment='选择字段')
    table_count = db.Column(db.Integer, default=0, comment='表数量')
    connection_status = db.Column(db.String(20), default='disconnected', comment='连接状态')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 定义与会话的关系
    conversations = db.relationship('Conversation', secondary='conversation_datasources', back_populates='datasources')
    
    def __repr__(self):
        return f"<DataSource {self.name}>"
    
    def to_dict(self):
        """转换为字典供API返回"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ds_type': self.ds_type,
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'include_views': self.include_views,
            'format': self.format,
            'table_count': self.table_count,
            'connection_status': self.connection_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': {
                'is_connected': self.connection_status == 'connected',
                'last_checked': self.updated_at.isoformat() if self.updated_at else None
            }
        }
    
    # 敏感信息不应在to_dict中返回密码
        
    def get_connection_string(self):
        """获取数据库连接字符串"""
        if self.ds_type.lower() == 'mysql':
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.ds_type.lower() == 'postgresql':
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.ds_type.lower() == 'oracle':
            return f"oracle+cx_oracle://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.ds_type.lower() == 'sqlserver':
            return f"mssql+pyodbc://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
        elif self.ds_type.lower() == 'kingbase':
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.ds_type}")


# 会话与数据源的多对多关系表
conversation_datasources = db.Table(
    'conversation_datasources',
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversations.id'), primary_key=True),
    db.Column('datasource_id', db.Integer, db.ForeignKey('datasources.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.now),
    extend_existing=True
) 