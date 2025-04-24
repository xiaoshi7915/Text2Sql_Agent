import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
class Config:
    # 应用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key_12345')
    DEBUG = False
    TESTING = False
    
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_NAME = os.getenv('DB_NAME', 'wenshu_mcp')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 大模型配置
    DEFAULT_LLM_MODEL = os.getenv('DEFAULT_LLM_MODEL', 'deepseek-chat')
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_API_BASE = os.getenv('LLM_API_BASE', 'https://api.deepseek.com')
    
    # MCP服务配置
    MCP_SERVER_HOST = os.getenv('MCP_SERVER_HOST', 'localhost')
    MCP_SERVER_PORT = os.getenv('MCP_SERVER_PORT', '5001')
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 跨域配置
    CORS_ORIGINS = ["*"]

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

# 测试环境配置
class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

# 生产环境配置
class ProductionConfig(Config):
    CORS_ORIGINS = [
        "https://wenshu-mcp.example.com",
        "https://api.wenshu-mcp.example.com"
    ]

# 配置字典
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 获取当前配置
def get_config():
    env = os.getenv('FLASK_ENV', 'default')
    return config_dict[env] 