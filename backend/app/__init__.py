"""
Flask应用初始化文件
"""

import os
import sys
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
    try:
        from api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError as e:
        print(f"无法导入API蓝图: {e}")
    
    # 创建所有表
    with app.app_context():
        db.create_all()
    
    return app 