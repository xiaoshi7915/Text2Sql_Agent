"""
Flask应用初始化文件
"""

import os
import sys
import logging
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# 确保路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建数据库对象
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 配置跨域资源共享
    CORS(app)
    
    # 配置数据库连接
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') or os.getenv('DATABASE_URL', 'sqlite:///wenshu.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 1天
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 注册蓝图
    from .api import datasources_bp
    app.register_blueprint(datasources_bp)
    
    # 注册兼容性蓝图 (处理旧路径请求)
    from .api import datasource_compat_bp
    app.register_blueprint(datasource_compat_bp)
    
    # 注册模型API蓝图
    from .api import model_bp
    app.register_blueprint(model_bp, url_prefix='/api/models')
    
    # 创建所有表
    with app.app_context():
        db.create_all()
    
    return app 