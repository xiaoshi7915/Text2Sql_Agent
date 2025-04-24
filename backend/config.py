"""
配置文件
包含开发和生产环境的配置信息
"""

import os

class Config:
    """基础配置类，包含所有环境通用的配置项"""
    # 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    # 其他通用配置
    
    @staticmethod
    def init_app(app):
        """初始化应用的配置"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 开发环境数据库URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost/wenshu_mcp'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    # 测试环境数据库URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost/wenshu_mcp_test'


class ProductionConfig(Config):
    """生产环境配置"""
    # 生产环境数据库URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost/wenshu_mcp'


# 配置字典，用于选择不同环境的配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 