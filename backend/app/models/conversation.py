from datetime import datetime
from . import db

class Conversation(db.Model):
    """用户与AI的会话模型"""
    
    __tablename__ = 'conversations'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=True, comment='会话标题')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID')
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=True, comment='使用的模型ID')
    is_active = db.Column(db.Boolean, default=True, comment='是否活跃')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    datasources = db.relationship('DataSource', secondary='conversation_datasources', back_populates='conversations')
    
    def __repr__(self):
        return f"<Conversation {self.id}>"
    
    def to_dict(self):
        """转换为字典供API返回"""
        return {
            'id': self.id,
            'title': self.title,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'is_active': self.is_active,
            'datasources': [ds.to_dict() for ds in self.datasources],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Message(db.Model):
    """会话中的消息模型"""
    
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False, comment='会话ID')
    role = db.Column(db.String(20), nullable=False, comment='消息角色(user/assistant/system)')
    content = db.Column(db.Text, nullable=False, comment='消息内容')
    sql_query = db.Column(db.Text, nullable=True, comment='生成的SQL查询语句')
    query_results = db.Column(db.JSON, nullable=True, comment='查询结果')
    error_message = db.Column(db.Text, nullable=True, comment='错误信息')
    tokens_used = db.Column(db.Integer, nullable=True, comment='使用的token数量')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    def __repr__(self):
        return f"<Message {self.id} ({self.role})>"
    
    def to_dict(self):
        """转换为字典供API返回"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'sql_query': self.sql_query,
            'query_results': self.query_results,
            'error_message': self.error_message,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 