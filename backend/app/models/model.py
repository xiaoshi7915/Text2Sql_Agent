from datetime import datetime
from . import db

class Model(db.Model):
    """大语言模型配置模型"""
    
    __tablename__ = 'models'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='模型名称')
    provider = db.Column(db.String(50), nullable=False, comment='模型提供商')
    model_type = db.Column(db.String(50), nullable=False, comment='模型类型')
    api_base = db.Column(db.String(255), nullable=True, comment='API基础URL')
    api_key = db.Column(db.String(255), nullable=True, comment='API密钥(加密存储)')
    api_version = db.Column(db.String(50), nullable=True, comment='API版本')
    temperature = db.Column(db.Float, default=0.7, comment='温度参数')
    max_tokens = db.Column(db.Integer, default=4096, comment='最大生成token数')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认模型')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    parameters = db.Column(db.JSON, nullable=True, comment='其他模型参数')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 与会话的关系
    conversations = db.relationship('Conversation', backref='model', lazy=True)
    
    def __repr__(self):
        return f"<Model {self.name}>"
    
    def to_dict(self):
        """转换为字典供API返回"""
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'model_type': self.model_type,
            'api_base': self.api_base,
            'api_version': self.api_version,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    # 不包含API密钥在to_dict中 